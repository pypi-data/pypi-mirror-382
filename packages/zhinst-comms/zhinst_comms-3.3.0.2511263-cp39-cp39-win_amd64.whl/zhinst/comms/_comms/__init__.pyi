"""Zurich Instruments communication protocol bindings."""

from __future__ import annotations
import typing
from . import compiler
from . import errors
from . import serialize

__all__ = [
    "Callback",
    "CapnpContext",
    "DEBUG",
    "DestinationParams",
    "DynamicClient",
    "DynamicEnum",
    "DynamicList",
    "DynamicServer",
    "DynamicStruct",
    "ERROR",
    "Fulfiller",
    "INFO",
    "InterfaceSchema",
    "LogSeverity",
    "STATUS",
    "SchemaLoader",
    "TRACE",
    "WARNING",
    "compiler",
    "errors",
    "init_logs",
    "serialize",
    "unwrap",
]

class HasStaticGetSchema(typing.Protocol):
    @staticmethod
    def get_schema() -> InterfaceSchema: ...

TypedClient = typing.TypeVar("TypedClient", bound=HasStaticGetSchema)

class Callback:
    """Registered Callback.

    This class wraps around an async function and allows passing it into
    the API.

    The signature of the function should be:

    ```python
        async def callback(
            interface_id: int,
            method_index: int,
            input: DynamicStruct,
            fulfiller: Fulfiller) -> None:
            ...
    ```

    The `input` contains the parameter the method was called with.
    The `fulfiller` is used to fulfill or reject the request. Note that
    the function must not return anything, but use the `fulfiller` to
    return the result. The reason for that is to allow the capnp thread
    to easily await the result, without having to deal with the async
    function directly.
    It the function returns or raises an exception, before the result is
    Fulfilled, that capnp request will hang forever. This should always
    be avoided.
    """

class CapnpContext:
    """Context responsible for managing Cap'n Proto connections.

    The CapnpContext is the main entry point into the capnp bindings. It
    can be used to initiate connections to a server or to spawn a server.
    """

    def __init__(self) -> None: ...
    def close(self) -> None:
        """Close the context and all associated clients/servers.

        Since python does not use RAII one can not know for sure when
        the context is going to be destroyed. If one wants to explicitly
        close all connections for both server and clients, e.g to free
        the port(s), this function can be used.

        Warning:
            All associated servers and sessions are closed. It is not
            guaranteed that all pending requests are processed.
            Pending futures will be rejected.
        """

    def connect(
        self,
        host: str,
        port: int,
        timeout: int = 5000,
        schema: InterfaceSchema | None = None,
    ) -> typing.Awaitable[DynamicClient]:
        """Connect to a capnp server.

        If no schema is provided, the reflection mechanism will be used to
        fetch the schema from the server.

        Args:
            host: The host to connect to.
            port: The port to connect to.
            timeout: The timeout in milliseconds for the connection
                attempt. (default: 5000ms)
            schema: The schema to use for the connection. If not provided,
                the schema will be fetched from the server.

        Returns:
            Connected client.
        """

    def connect_labone(
        self,
        host: str,
        port: int,
        destination: DestinationParams | None,
        timeout: int = 5000,
        schema: InterfaceSchema | None = None,
    ) -> typing.Awaitable[DynamicClient]:
        """Connect to a LabOne server.

        If no schema is provided, the reflection mechanism will be used to
        fetch the schema from the server.

        Args:
            host: The LabOne host.
            port: The LabOne port.
            destination: Parameter specifying the target kernel.
            timeout: The timeout in milliseconds for the connection
                attempt. (default: 5000ms)
            schema: The schema to use for the connection. If not provided,
                the schema will be fetched from the server.

        Returns:
            Connected client.
        """

    async def connect_url(
        self: CapnpContext,
        url: str,
        timeout: int = 1500,
        max_retries: int = 5,
        schema: InterfaceSchema | typing.Type[TypedClient] | None = None,
    ) -> DynamicClient | TypedClient:
        """Connect to a capnp server using a URL

        If the URL scheme is "tcp" the destination is assumed to be
        a capnp server and a direct connection is made.

        If the URL doesn't have a scheme, but it's in the format "host:port"
        (e.g. localhost:8004), the scheme is inferred to be tcp.

        If the scheme is "http", the destination is assumed to be an HTTP server.
        The server is expected to respond with a redirect to the actual location
        of the capnp server.

        Important: this function cannot be used to connect to a LabOne data-server.
        For that, use the dedicated "connect_labone" function.

        Args:
            url: destination to connect to
            timeout: The timeout in milliseconds for the connection
                attempt. (default: 1500 ms)
            max_retries: how many times can a connection be attempted before giving up
            schema: The schema to use for the connection. If not provided,
                the schema will be fetched from the server. A client class from a _schema.py
                file can also be provided directly.

        Returns:
            Connected client.

        Warning:
            At the moment, there is no automatic check that the provided schema actually matches
            the interface served by the server.
        """

    def create_pipe(
        self, server_callback: typing.Any, schema: InterfaceSchema
    ) -> typing.Awaitable[typing.Tuple[DynamicServer, DynamicClient]]:
        """Create a Server Client pair through a two way pipe.

        Both the server and the client will be fully functional.

        Args:
            server_callback: Async callback invoked whenever a request is
                made.
            schema: The schema for interface the server implements.

        Returns:
            server, client pair.
        """

    def listen(
        self,
        port: int,
        openOverride: bool,
        callback: typing.Callable,
        schema: InterfaceSchema,
    ) -> typing.Awaitable[DynamicServer]:
        """Spawn a server.

        The server is a fully functional capnp server that implements the
        provided interface.
        Every request will trigger a call to the provided callback. The
        Signature of the callback is
        (interface_id, method_index, input, fulfiller) -> None
        For more information see the documentation of the callback.

        Args:
            port: The port the server should listen to.
            openOverride: Flag if the server should be local or also open
                to the network.
            callback: Async callback invoked whenever a request is made.
            schema: The schema for interface the server implements.

        Returns:
            Created server. The underlying capnp server will be destroyed
            when the server object is destroyed.
        """

    def register_callback(self, callback: typing.Any) -> Callback:
        """Register a callback function.

        This guarantees the proper lifetime handling even if the callback
        is later transferred to capnp.

        Args:
            callback: Async callback that needs to be passed to capnp.
        Returns:
            Reference to the managed callback.
        """

class DestinationParams:
    @staticmethod
    def device_connection(device_id: str, interface: str = "") -> DestinationParams:
        """Create the destination params for a connection to a device.

        Args:
            device_id: The device serial.
            interface: The interface that data server should use to
                establish the connection. If empty the data server will
                use the default interface. (default = "")

        Returns:
            Destination parameters for the connection.
        """

    @staticmethod
    def zi_connection() -> DestinationParams:
        """Create the destination params for a connection to a LabOne Orchestrator.

        Returns:
            Destination parameters for the connection.
        """

class DynamicClient:
    """Client connection to a capnp server.

    The available methods are dynamically determined provided interface.
    The `dir` function can be used to list the available methods.

    The available methods have the same signature as the server interface.
    The input is a kwargs dictionary with the required arguments.
    The return value is a future object that can be awaited to get the
    result.

    Example:
    ```python
        result = await session.setValue(
            pathExpression = "hwmock/ints/0/value",
            value = {"int64" : 48},
    )
    """

    def __getattr__(
        self, arg0: str
    ) -> typing.Callable[..., typing.Awaitable[DynamicStruct]]: ...
    def close(self) -> None:
        """Close the underlying connection to the capnp server.

        Since python does not use RAII one can not know for sure when
        the client is going to be destroyed. If one wants to explicitly
        close the connection to the server, this function can be used.
        """

class DynamicEnum:
    """Holds a capnp enum value.

    This object can not be created within Python but is returned by the
    package.

    The enum can be converted to a string or to an its raw integer value.
    For simplicity, the enum can be compared to a string or an integer as well.
    """

    @typing.overload
    def __eq__(self, arg0: DynamicEnum) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: str) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: int) -> bool: ...
    def __hash__(self) -> int: ...
    def __str__(self) -> str: ...
    @property
    def raw(self) -> int:
        """Raw integer value of the enum."""

class DynamicList:
    """Holds a capnp list value.

    This object can not be created within Python but is returned by the
    package.

    Can be used as any other list object.
    """

    def __getitem__(self, arg0: int) -> typing.Any: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg0: int, arg1: typing.Any) -> None: ...
    def __str__(self) -> str: ...

class DynamicServer:
    """Capnp server instance.

    The server can not be created directly but only through the context.
    """

    def close(self) -> None:
        """Close the underlying socket.

        Since python does not use RAII one can not know for sure when
        the server is going to be destroyed. If one wants to explicitly
        close the socket,e.g to free the port, this function can be used.
        """

    @property
    def port(self) -> int:
        """Return the port this server is listening on."""

class DynamicStruct:
    """Holds a capnp struct value.

    Its fields can be accessed as attributes or items. It also supports
    similar functionalities, like iteration, one would expect from a dict.

    Its main purpose is to hold the result of a capnp rpc call. However, it is
    mutable and can also be instantiated within python.

    Args:
        schema_loader: The schema loader that holds the schema of the struct.
        struct_id: The id of the struct.
        kwargs: Optional initial values of the fields.
    """

    def __init__(
        self, schema_loader: SchemaLoader, struct_id: int, **kwargs: typing.Any
    ) -> None: ...
    def __contains__(self, arg0: str) -> bool: ...
    def __getattr__(self, arg0: str) -> typing.Any: ...
    def __getitem__(self, arg0: str) -> typing.Any: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    def __setattr__(self, arg0: str, arg1: typing.Any) -> None: ...
    def __setitem__(self, arg0: str, arg1: typing.Any) -> None: ...
    def __str__(self) -> str: ...
    def get_union_element(self) -> typing.Any:
        """Get the union element.

        If the struct is a union, this function will return the active element.
        If the struct is not a union, an exception will be raised.

        Returns:
            The active element.

        Raises:
            AttributeError: If the struct does not contain a union.
        """

    def get_union_element_name(self) -> str:
        """Get the name of the union element.

        If the struct is a union, this function will return the name of the
        active element. If the struct is not a union, an exception will be raised.

        Returns:
            The name of the active element.

        Raises:
            AttributeError: If the struct does not contain a union.
        """

    def init_list(self, name: str, size: int) -> DynamicList:
        """Initialize a list field.

        Fields of type struct and list are not initialized by default within
        capnp. In order to use them, they need to be initialized first.

        This function initializes a list field with the given size and returns
        the list object. After the list is initialized it can be accessed directly
        through the struct.

        Args:
            name: The name of the list field.
            size: The size of the list.
        """

    def init_struct(self, name: str, **kwargs: typing.Any) -> DynamicStruct:
        """Initialize a struct field.

        Fields of type struct and list are not initialized by default within
        capnp. In order to use them, they need to be initialized first.

        This function initializes a struct field and returns the struct object.
        After the struct is initialized it can be accessed directly
        through the parent struct.

        Args:
            name: The name of the struct field.
            kwargs: Optional initial values of the struct fields.
        """

    def keys(self) -> list[str]:
        """Return the available field names."""

    def to_json(self) -> str:
        """Convert the struct to a json string.

        Note that since the Cap'n Proto JSON codec is used the result may
        differ compared to the native python JSON format. The advantage is that
        the result can be directly used be used by any other Cap'n Proto logic.

        Returns:
            The json string.
        """

    def to_packed_capnp(self) -> bytes:
        """Convert the struct to a packed capnp byte string.

        Returns:
            The packed capnp byte string.
        """

    @property
    def capnp_id(self) -> int:
        """The capnp id of the struct."""

class Fulfiller:
    """Fulfiller of a request.

    A Fulfiller is used to fulfill or reject a request. The result will
    be send back to the caller through capnp.
    """

    class RejectReason:
        """Reason for rejecting a promise.
        This information can be used by the client to decide how to handle the
        rejection.

        Members:
            FAILED : Something went wrong. This is the usual reject reason.
            OVERLOADED : The call failed because of a temporary lack of resources.
                This could be space resources (out of memory, out of disk space) or
                time resources (request queue overflow, operation timed out).
                The operation might work if tried again, but it should NOT be
                repeated immediately as this may simply exacerbate the problem.
            DISCONNECTED : The call required communication over a connection that
                has been lost. The callee will need to re-establish connections
                and try again.
            UNIMPLEMENTED : The requested method is not implemented. The caller
                may wish to revert to a fallback approach based on other methods.
        """

        DISCONNECTED: typing.ClassVar[
            Fulfiller.RejectReason
        ]  # value = <RejectReason.DISCONNECTED: 2>
        FAILED: typing.ClassVar[
            Fulfiller.RejectReason
        ]  # value = <RejectReason.FAILED: 0>
        OVERLOADED: typing.ClassVar[
            Fulfiller.RejectReason
        ]  # value = <RejectReason.OVERLOADED: 1>
        UNIMPLEMENTED: typing.ClassVar[
            Fulfiller.RejectReason
        ]  # value = <RejectReason.UNIMPLEMENTED: 3>
        __members__: typing.ClassVar[
            dict[str, Fulfiller.RejectReason]
        ]  # value = {'FAILED': <RejectReason.FAILED: 0>, 'OVERLOADED': <RejectReason.OVERLOADED: 1>, 'DISCONNECTED': <RejectReason.DISCONNECTED: 2>, 'UNIMPLEMENTED': <RejectReason.UNIMPLEMENTED: 3>}
        def __eq__(self, other: typing.Any) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
        def __init__(self, value: int) -> None: ...
        def __int__(self) -> int: ...
        def __ne__(self, other: typing.Any) -> bool: ...
        def __repr__(self) -> str: ...
        def __setstate__(self, state: int) -> None: ...
        def __str__(self) -> str: ...
        @property
        def name(self) -> str: ...
        @property
        def value(self) -> int: ...

    DISCONNECTED: typing.ClassVar[
        Fulfiller.RejectReason
    ]  # value = <RejectReason.DISCONNECTED: 2>
    FAILED: typing.ClassVar[Fulfiller.RejectReason]  # value = <RejectReason.FAILED: 0>
    OVERLOADED: typing.ClassVar[
        Fulfiller.RejectReason
    ]  # value = <RejectReason.OVERLOADED: 1>
    UNIMPLEMENTED: typing.ClassVar[
        Fulfiller.RejectReason
    ]  # value = <RejectReason.UNIMPLEMENTED: 3>
    def fulfill(self, dict: typing.Dict = None, **kwargs: typing.Any) -> None:
        """The data is passed as a dictionary.

        Optionally, the data can be passed as keyword arguments.
        """

    def reject(self, reason: Fulfiller.RejectReason, message: str) -> None:
        """Reject the request.

        Args:
            reason: The reason for rejecting the request.
            message: A message that describes the reason for rejecting the
                request.
        """

class InterfaceSchema:
    """Python representation of a capnp interface schema.

    Note that this class can only be instantiated through the SchemaLoader.

    Capnp requires that both client and server know the schema of the
    interface they are communicating with. All Zurich Instruments
    servers, including the one spawned with this package support the
    reflection interface. Meaning the client can request the schema from
    the server. However, this has some significant downsides, e.g. the
    client needs to rely on the server not changing the interface.
    Therefore, it is recommended to hardcode the used schema in the
    client and thus ensuring backwards compatibility.
    """

class LogSeverity:
    """Log Severity of the capnp bindings.

    Members:
        TRACE
        DEBUG
        INFO
        STATUS
        WARNING
        ERROR
    """

    DEBUG: typing.ClassVar[LogSeverity]  # value = <LogSeverity.DEBUG: 1>
    ERROR: typing.ClassVar[LogSeverity]  # value = <LogSeverity.ERROR: 5>
    INFO: typing.ClassVar[LogSeverity]  # value = <LogSeverity.INFO: 2>
    STATUS: typing.ClassVar[LogSeverity]  # value = <LogSeverity.STATUS: 3>
    TRACE: typing.ClassVar[LogSeverity]  # value = <LogSeverity.TRACE: 0>
    WARNING: typing.ClassVar[LogSeverity]  # value = <LogSeverity.WARNING: 4>
    __members__: typing.ClassVar[
        dict[str, LogSeverity]
    ]  # value = {'TRACE': <LogSeverity.TRACE: 0>, 'DEBUG': <LogSeverity.DEBUG: 1>, 'INFO': <LogSeverity.INFO: 2>, 'STATUS': <LogSeverity.STATUS: 3>, 'WARNING': <LogSeverity.WARNING: 4>, 'ERROR': <LogSeverity.ERROR: 5>}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class SchemaLoader:
    """Load capnp schemas from a byte string.

    The SchemaLoader can be used to load the schema from a byte string and
    provide the interface schema to the server and the client.

    Capnp requires that both client and server know the schema of the
    interface they are communicating with. All Zurich Instruments
    servers, including the one spawned with this package support the
    reflection interface. Meaning the client can request the schema from
    the server. However, this has some significant downsides, e.g. the
    client needs to rely on the server not changing the interface.
    Therefore, it is recommended to hardcode the used schema in the
    client and thus ensuring backwards compatibility.

    Args:
       schema: The schema as a byte string (precompiled capnp schema).
       version: The version of the schema. (default = "")
    """

    def __init__(self, schema: str, version: str = "") -> None: ...
    def get_interface_schema(self, schema_id: int) -> InterfaceSchema:
        """Get the schema for a specific interface.

        Note that the schema must be part of the provided schema. If not an
        exception will be raised.

        Args:
            schema_id: The id of the interface schema.

        Returns:
            The interface schema.

        Raises:
            KeyError: If the schema_id is not part of the provided schema.
        """

def init_logs(severity: LogSeverity = ...) -> None:
    """Initialize the logging system.

    Currently, the default LabOne logging system is used. The log messages
    will be logged to the console and the log file (CapnpBindings).

    Args:
        severity: The log level to set. (default = INFO)
    """

def unwrap(input_value: DynamicStruct) -> DynamicStruct:
    """Unwrap a ZI result struct.

    The Result struct is something specific to ZI and not a capnp feature.
    This helper function will attempt to unwrap the result struct and return
    The inner content. If the Result contains an Error it will be raised

    If the input is not a result struct, the input will be returned untouched.

    Args:
        input_value: Object to unwrap.

    Returns:
        Unwrapped data if the input is a Result struct otherwise the original
        Input.
    """

DEBUG: LogSeverity  # value = <LogSeverity.DEBUG: 1>
ERROR: LogSeverity  # value = <LogSeverity.ERROR: 5>
INFO: LogSeverity  # value = <LogSeverity.INFO: 2>
STATUS: LogSeverity  # value = <LogSeverity.STATUS: 3>
TRACE: LogSeverity  # value = <LogSeverity.TRACE: 0>
WARNING: LogSeverity  # value = <LogSeverity.WARNING: 4>
__commit_hash__: str = "26b0489d80dbb747036ddd48f0901a5b79c858a1"
__version__: str = "3.0.0"
