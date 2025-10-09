"""Capnp server base implementation."""

from __future__ import annotations

import typing as t
from asyncio import Future, get_running_loop
from functools import partial
from signal import SIGINT, SIGTERM, Signals

import zhinst.comms
from typing_extensions import TypeAlias

CapnpResult: TypeAlias = dict[str, t.Any]


def capnp_method(interface: int, method_index: int) -> t.Callable:
    """A decorator indicate that a function is capnp callback."""

    def inner(func: t.Callable) -> t.Callable:
        func._capnp_info = (  # type:ignore[attr-defined]  # noqa: SLF001
            interface,
            method_index,
        )
        return func

    return inner


class CapnpServer:
    """Basic capnp server.

    This class provides the basic interface for a capnp server. It is
    designed to be subclassed and the subclass should implement the
    server specific functionality. The CapnpServer class hides the mechanics
    of the how zhinst.comms interfaces with python and implements all the
    necessary boilerplate code.

    The only things needed to be implemented are the methods defined in the
    schema. These methods need to be decorated with the capnp_method decorator.
    The decorator takes the interface id and the method index from the
    capnp schema as arguments. The method itself is a coroutine that takes
    the input of the capnp call and returns the output as dictionary.

    Example:

        Given the following schema:
        ```
        interface DummyInterface @0x1234567890 {
            method echoSomeText @0 () -> (text: Text);
        }
        ```

        The corresponding python code would look like this:

        ```python
        class DummyServer(CapnpServer):
            @capnp_method(0x1234567890, 0)
            async def echo(self, input: zhinst.comms.DynamicStruct) -> CapnpResult:
                return {"text": input["text"]}
        ```

    Note the following things:

    - The method name does not have to match the method name in the schema. The
      identifier is the capnp_method decorator.
    - Every exception raised will be caught and translated to a capnp disconnect
      error. This will result in most clients to close the connection.
    - If a method is not defines a UNIMPLEMENTED error will be returned to the
      client.

    Args:
        schema: interface schema to use.
    """

    def __init__(self, schema: zhinst.comms.InterfaceSchema):
        self._schema = schema
        self._registered_callbacks: dict[tuple[int, int], t.Callable] = {}
        self._run_forever_future: Future[None] | None = None
        self._capnp_server: zhinst.comms.DynamicServer | None = None
        self._load_callbacks()

    def _load_callbacks(self) -> None:
        """Load all methods with the capnp_method decorator."""
        for method_name in dir(self):
            method = getattr(self, method_name)
            capnp_info = getattr(method, "_capnp_info", None)
            if capnp_info:
                self._registered_callbacks[capnp_info] = method

    async def _capnp_callback(
        self,
        interface: int,
        method_index: int,
        call_input: zhinst.comms.DynamicStruct,
        fulfiller: zhinst.comms.Fulfiller,
    ) -> None:
        """Entrypoint for all capnp calls.

        This method called by capnp whenever a new request is received.

        Args:
            interface: Interface of the call.
            method_index: Method index of the call.
            call_input: Input of the call.
            fulfiller: Fulfiller to fulfill or reject the call.
        """
        target_info = (interface, method_index)
        if target_info not in self._registered_callbacks:
            fulfiller.reject(
                zhinst.comms.Fulfiller.UNIMPLEMENTED,
                f"Function {interface}:{method_index} not implemented",
            )
            return
        try:
            fulfiller.fulfill(await self._registered_callbacks[target_info](call_input))
        except Exception as e:  # noqa: BLE001
            fulfiller.reject(zhinst.comms.Fulfiller.DISCONNECTED, str(e.args[0]))

    async def start(
        self,
        port: int,
        *,
        open_overwrite: bool = False,
        context: zhinst.comms.CapnpContext,
    ) -> None:
        """Start the server on a given port.

        Args:
            context: context to use.
            port: port to listen on.
            open_overwrite: Flag if the server should be reachable from outside.
        """
        if self._capnp_server:
            msg = f"server {self!r} is already running"
            raise zhinst.comms.errors.BaseError(msg)
        self._capnp_server = await context.listen(
            port=port,
            openOverride=open_overwrite,
            callback=self._capnp_callback,
            schema=self._schema,
        )

    def close(self) -> None:
        """Close the server."""
        if self._capnp_server is None:
            msg = f"server {self!r} is not running"
            raise zhinst.comms.errors.BaseError(msg)
        self._capnp_server.close()

    async def run_forever(self) -> None:
        """Run the server forever.

        Useful for running the server in the main thread.

        This method is a coroutine that will block until the server until a
        CancelledError is raised. After a CancelledError the server is shutdown
        properly and the functions returns.
        """
        if self._run_forever_future is not None:
            msg = f"server {self!r} is already being awaited on run_forever()"
            raise zhinst.comms.errors.BaseError(msg)
        if self._capnp_server is None:
            msg = f"server {self!r} is not running"
            raise zhinst.comms.errors.BaseError(msg)

        self._run_forever_future = get_running_loop().create_future()

        def signal_handler(signal: Signals, future: Future[None]) -> None:
            loop.remove_signal_handler(signal)
            future.cancel()

        loop = get_running_loop()
        for signal_enum in [SIGINT, SIGTERM]:
            loop.add_signal_handler(
                signal_enum,
                partial(signal_handler, signal_enum, self._run_forever_future),
            )

        try:
            await self._run_forever_future
        finally:
            self.close()
            self._run_forever_future = None

    async def start_pipe(
        self,
        context: zhinst.comms.CapnpContext,
    ) -> zhinst.comms.DynamicClient:
        """Create a local pipe to the server.

        A pipe is a local single connection to the server.

        Args:
            context: context to use.
        """
        self._capnp_server, client = await context.create_pipe(
            server_callback=self._capnp_callback,
            schema=self._schema,
        )
        return client

    @property
    def port(self) -> int:
        """Return the port the server is listening on"""
        try:
            return self._capnp_server.port
        except AttributeError:
            return 0
