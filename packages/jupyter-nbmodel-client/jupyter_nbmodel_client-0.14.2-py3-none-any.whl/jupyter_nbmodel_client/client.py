# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Coroutine
from functools import partial
from typing import Any, Callable, cast
from urllib.parse import urlparse

from pycrdt import (
    Awareness,
    TransactionEvent,
    YMessageType,
    YSyncMessageType,
    create_awareness_message,
    create_sync_message,
    create_update_message,
    handle_sync_message,
)
from websockets.asyncio.client import ClientConnection, connect

from jupyter_nbmodel_client._version import VERSION
from jupyter_nbmodel_client.constants import DEFAULT_LOGGER, REQUEST_TIMEOUT
from jupyter_nbmodel_client.model import NotebookModel

# Default value taken from uvicorn: https://www.uvicorn.org/#command-line-options
# Note: the default size for Tornado is 10MB not 16MB
WEBSOCKETS_MAX_BODY_SIZE = int(os.environ.get("WEBSOCKETS_MAX_BODY_SIZE", 16 * 1024 * 1024))


def _on_doc_update(
    queue: asyncio.Queue,
    event: TransactionEvent,
) -> None:
    message = create_update_message(event.update)
    queue.put_nowait(message)


def _on_awareness_event(
    awareness: Awareness,
    queue: asyncio.Queue,
    event_type: str,
    changes: tuple[dict[str, Any], Any],
) -> None:
    # Skip non-update awareness changes and non-local changes;
    # aka broadcast only local update
    if event_type != "update" or changes[1] != "local":
        return

    updated_clients = [v for value in changes[0].values() for v in value]
    state = awareness.encode_awareness_update(updated_clients)
    message = create_awareness_message(state)

    queue.put_nowait(message)


async def _send_messages(
    websocket: ClientConnection,
    logger: logging.Logger,
    queue: asyncio.Queue[bytes],
) -> None:
    while True:
        message = None
        try:
            message = await queue.get()
            logger.debug("Forwarding message [%s]", message)
            await websocket.send(message)
            queue.task_done()  # Mark task as done for queue.join()
        except asyncio.CancelledError:
            # Only call task_done if we actually got a message from the queue
            if message is not None:
                queue.task_done()
            raise
        except BaseException as e:
            logger.error(
                "Failed to forward message to websocket. Queue size: %s",
                queue.qsize(),
                exc_info=e,
            )
            # Only call task_done if we actually got a message from the queue
            if message is not None:
                queue.task_done()
            raise


async def _listen_to_websocket(
    websocket: ClientConnection,
    logger: logging.Logger,
    on_message: Callable[[bytes], Coroutine[None, None, None]],
) -> None:
    while True:
        try:
            async for message in websocket:
                logger.debug("Received message [%s]", message)
                await on_message(message)
        except asyncio.CancelledError:
            raise
        except BaseException as e:
            logger.error("Websocket client stopped.", exc_info=e)
            raise


class NbModelClient(NotebookModel):
    """Client to one Jupyter notebook model.

    Args:
        ws_url: Endpoint to connect to the collaborative Jupyter notebook.
        path: [optional] Notebook path relative to the server root directory; default None
        username: [optional] Client user name; default to environment variable USER
        timeout: [optional] Request timeout in seconds; default to environment variable REQUEST_TIMEOUT
        log: [optional] Custom logger; default local logger
        ws_max_body_size: [optional] Maximum WebSocket body size in bytes; default 16MB
        close_timeout: [optional] Timeout for propagating final changes on close; default to timeout value

    Examples:

    When connection to a Jupyter notebook server, you can leverage the get_jupyter_notebook_websocket_url
    helper:

    >>> from jupyter_nbmodel_client import NbModelClient, get_jupyter_notebook_websocket_url
    >>> ws_url = get_jupyter_notebook_websocket_url(
    >>>     "http://localhost:8888",
    >>>     "path/to/notebook.ipynb",
    >>>     "your-server-token"
    >>> )
    >>> client = NbModelClient(ws_url)
    """

    # Code logic
    #
    # The client has at its core a `run` asynchronous method that work similarly as the function you
    # would execute in a another thread.
    # In that method, the websocket connection will be opened and background tasks transfering and
    # processing the messages coming from the websocket and the document model changes will be
    # created.
    # When the method `run` is canceled, all the background tasks will be canceled as well and
    # the connection will be closed.
    #
    # Document changes callback is only placing event in a queue as it is a blocking operation.
    #
    # When using the nbmodel client as a context manager or the start/stop methods, the `run` method will be
    # executed in a task.

    user_agent: str = f"Datalayer-NbModelClient/{VERSION}"
    """User agent used to identify the nbmodel client type in the awareness state."""


    def __init__(
        self,
        websocket_url: str,
        path: str | None = None,
        username: str = os.environ.get("USER", "username"),
        timeout: float = REQUEST_TIMEOUT,
        log: logging.Logger | None = None,
        ws_max_body_size: int | None = None,
        close_timeout: float | None = None,
    ) -> None:
        super().__init__()
        self._ws_url = websocket_url
        self._path = path or websocket_url
        self._username = username
        self._timeout = timeout
        self._log = log or DEFAULT_LOGGER
        self._ws_max_body_size = ws_max_body_size or WEBSOCKETS_MAX_BODY_SIZE
        self._close_timeout = close_timeout if close_timeout is not None else timeout

        self.__synced = asyncio.Event()
        self.__run: asyncio.Task | None = None
        self.__is_running = False


    @property
    def path(self) -> str:
        """Document path relative to the server root path."""
        return self._path

    @property
    def server_url(self) -> str:
        """Client server url."""
        parsed_url = urlparse(self._ws_url)
        cleaned_url = parsed_url._replace(query="", fragment="", params="")
        return cleaned_url.geturl()

    @property
    def synced(self) -> bool:
        """Whether the model is synced or not."""
        return self.__synced.is_set()

    @property
    def username(self) -> str:
        """Client owner username."""
        return self._username


    def __del__(self) -> None:
        if self.__run is not None:
            self.__run.cancel()  # Theoritically, this should be awaited

    async def __aenter__(self) -> "NbModelClient":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> None:
        await self.stop()


    async def run(self) -> None:
        """Run the nbmodel client."""
        self._log.info("Starting the nbmodel client…")
        if self.__is_running:
            raise RuntimeError("NbModelClient is already connected.")

        self.__is_running = True
        self._log.debug("Starting the websocket connection…")

        websocket = await connect(
            self._ws_url,
            user_agent_header="Jupyter NbModel Client",
            logger=self._log,
            max_size=self._ws_max_body_size,
        )
        messages_queue: asyncio.Queue[bytes] = asyncio.Queue()

        # Start listening to incoming message
        listener = asyncio.create_task(
            _listen_to_websocket(
                logger=self._log,
                on_message=partial(self._on_message, websocket),
                websocket=websocket,
            )
        )

        # Start listening for doc changes
        doc_observer = self._doc.ydoc.observe(partial(_on_doc_update, messages_queue))

        # Start listening for awareness updates
        awareness_observer = cast(Awareness, self._doc.awareness).observe(
            partial(_on_awareness_event, cast(Awareness, self._doc.awareness), messages_queue)
        )

        # Set local state
        self.set_local_state_field(
            "user",
            {
                "agent": self.user_agent,
                "owner": self._username,
                "address": str(websocket.remote_address),
            },
        )

        # Start the awareness regular ping
        awareness_ping = asyncio.create_task(self._doc.awareness._start())

        # Start forwarding document and awareness messages through the websocket
        sender = asyncio.create_task(
            _send_messages(logger=self._log, websocket=websocket, queue=messages_queue)
        )

        # Synchronize the model
        with self._lock:
            sync_message = create_sync_message(self._doc.ydoc)
        self._log.debug(
            "Sending SYNC_STEP1 message for document %s",
            self._path,
        )
        await websocket.send(sync_message)

        try:
            # Wait forever and prevent the forwarder to be cancelled to avoid losing changes
            await asyncio.gather(awareness_ping, listener, asyncio.shield(sender))
        finally:
            self._log.info("Stopping the nbmodel client…")

            # Step 1: Stop listening to incoming messages (prevent new messages from server)
            self._log.debug("Stopping listening to incoming messages…")
            if listener.cancel():
                await asyncio.wait([listener])

            # Step 2: Stop document and awareness observers (prevent new local changes)
            self._log.debug("Stopping listening for awareness update…")
            cast(Awareness, self._doc.awareness).unobserve(awareness_observer)

            self._log.debug("Stopping listening for document changes…")
            try:
                self._doc.ydoc.unobserve(doc_observer)
            except ValueError as e:
                if str(e) != "list.remove(x): x not in list":
                    self._log.error("Failed to unobserve the notebook model.", exc_info=e)

            # Step 3: Wait for message queue to be empty (with timeout protection)
            self._log.debug("Trying to propagate the last changes…")
            if not sender.done():
                if not messages_queue.empty():
                    self._log.info("Propagating %s last changes…", messages_queue.qsize())
                    try:
                        # Use timeout to avoid hanging indefinitely
                        await asyncio.wait_for(
                            asyncio.shield(messages_queue.join()),
                            timeout=self._close_timeout,
                        )
                        self._log.info("All changes propagated successfully.")
                    except asyncio.TimeoutError:
                        self._log.warning(
                            "Timeout while propagating last %s changes. Some changes may be lost.",
                            messages_queue.qsize(),
                        )

                # Step 4: Stop the sender task (now that queue is empty or timed out)
                self._log.debug("Stopping forwarding task…")
                if sender.cancel():
                    await asyncio.wait([sender])

            # Step 5: Stop awareness ping
            if not awareness_ping.done():
                self._log.debug("Stopping awareness ping…")
                awareness_ping.cancel()
                await asyncio.wait([awareness_ping])

            # Step 6: Reset the model
            self._log.debug("Resetting the model…")
            self._reset_y_model()
            self.__synced.clear()

            # Step 7: Close the websocket (last step to ensure all messages are sent)
            self._log.debug("Closing the websocket…")
            if websocket:
                try:
                    await websocket.close()
                except BaseException as e:
                    self._log.error("Unable to close the websocket connection.", exc_info=e)
                    raise
                finally:
                    self._log.info("Websocket connection closed.")
                    websocket = None

            self.__is_running = False


    def get_local_client_id(self) -> int:
        """Get the local client ID.

        This is the identifier of the nbmodel client communicated to all peers.

        Returns:
            The local client ID.
        """
        return cast(Awareness, self._doc.awareness).client_id

    def get_connected_peers(self) -> list[int]:
        """Get the connected peer client IDs.

        Returns:
            A list of the connected peer client IDs.
        """
        local_id = self.get_local_client_id()
        return [
            client_id
            for client_id in cast(Awareness, self._doc.awareness).states
            if client_id != local_id
        ]

    def get_peer_state(self, client_id: int) -> dict[str, Any] | None:
        """Get the connected peer client states.

        Returns:
            A dictionary of the connected peer client states.
        """
        return cast(Awareness, self._doc.awareness).states.get(client_id)

    def set_local_state_field(self, key: str, value: Any) -> None:
        """Sets a local state field to be shared between peer clients.

        Args:
            field: The field of the local state to set.
            value: The value associated with the field.
        """
        cast(Awareness, self._doc.awareness).set_local_state_field(key, value)


    async def start(self) -> None:
        """Start the nbmodel client."""
        if self.__run is not None:
            raise RuntimeError("The client is already connected.")

        self.__run = asyncio.create_task(self.run())

        def callback(_: asyncio.Task) -> None:
            self.__run = None

        self.__run.add_done_callback(callback)

        self._log.debug("Waiting for model synchronization…")
        try:
            await asyncio.wait_for(self.__synced.wait(), REQUEST_TIMEOUT)
        except asyncio.TimeoutError:
            ...
        if not self.synced:
            self._log.warning("Document %s not yet synced.", self._path)


    async def stop(self) -> None:
        """Stop and reset the nbmodel client."""
        if self.__run is not None:
            if self.__run.cancel():
                await asyncio.wait([self.__run])


    async def wait_until_synced(self) -> None:
        """Wait until the model is synced."""
        await self.__synced.wait()


    async def _on_message(self, websocket: ClientConnection, message: bytes) -> None:
        if message[0] == YMessageType.SYNC:
            self._log.debug(
                "Received %s message from document %s",
                YSyncMessageType(message[1]).name,
                self._path,
            )
            with self._lock:
                reply = handle_sync_message(message[1:], self._doc.ydoc)
            if message[1] == YSyncMessageType.SYNC_STEP2:
                self.__synced.set()
                self._fix_model()
            if reply is not None:
                self._log.debug(
                    "Sending SYNC_STEP2 message to document %s",
                    self._path,
                )
                await websocket.send(reply)
