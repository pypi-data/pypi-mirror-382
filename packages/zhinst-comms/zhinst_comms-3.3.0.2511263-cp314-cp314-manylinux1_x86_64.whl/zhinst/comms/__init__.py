from typing import Type, Optional, TypeVar, Protocol
import urllib.parse
from ._comms import *
from ._comms.errors import BadRequestError, BaseError, TimeoutError, UnavailableError
import aiohttp
import asyncio
import re

__doc__ = _comms.__doc__
__version__ = _comms.__version__
__commit_hash__ = _comms.__commit_hash__

if hasattr(_comms, "__all__"):
    __all__ = _comms.__all__


class HasStaticGetSchema(Protocol):
    @staticmethod
    def get_schema() -> InterfaceSchema: ...


TypedClient = TypeVar("TypedClient", bound=HasStaticGetSchema)


async def connect_url(
    self: CapnpContext,
    url: str,
    timeout: int = 1500,
    max_retries: int = 5,
    schema: InterfaceSchema | Type[TypedClient] | None = None,
) -> DynamicClient | Type[TypedClient]:
    def get_schema_if_available() -> Optional[InterfaceSchema]:
        if isinstance(schema, InterfaceSchema):
            return schema
        if schema is not None:
            return schema.get_schema()
        return None

    async def retry(f, retry_immediately_exception, retry_later_exception):
        for trial in range(max_retries + 1):
            try:
                return await f()
            except Exception as e:
                if trial >= max_retries:
                    raise
                elif isinstance(e, retry_immediately_exception):
                    continue
                elif isinstance(e, retry_later_exception):
                    await asyncio.sleep(float(timeout) / 1000.0)
                    continue
                else:
                    raise

    def parse_url(url: str) -> urllib.parse.ParseResult:
        # URL in the format host:port, without scheme, is accepted and assumed to be TCP
        if re.fullmatch("[a-zA-Z0-9-.]+:[0-9]+", url):
            url = "tcp://" + url
        # We check the scheme manually because the scheme inferred by the url parsing
        # can be confusing also in seemingly benign cases. For example, the scheme of
        # "127.0.0.1:8080" is "127.0.0.1"
        if not (url.startswith("http://") or url.startswith("tcp://")):
            raise BadRequestError(
                f"Cannot connect using url {url}. The url should start with http://, or tcp://"
            )
        return urllib.parse.urlparse(url)

    async def do_tcp_connect(parsed_url: urllib.parse.ParseResult):
        parts = parsed_url.netloc.split(":")
        if len(parts) != 2:
            raise BadRequestError(f"Cannot infer host and port from url {url}.")
        try:
            port = int(parts[1])
        except ValueError:
            raise BadRequestError(f"{parts[1]} is not a valid port number.")
        host = parts[0]
        return await retry(
            lambda: self.connect(host, port, timeout, get_schema_if_available()),
            TimeoutError,
            UnavailableError,
        )

    async def http_connect_with_retry(session: aiohttp.ClientSession):
        async def send():
            async with session.get(
                url,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=float(timeout) / 1000),
            ) as response:
                response.raise_for_status()
                return response.status, response.headers.get("Location")

        try:
            return await retry(send, asyncio.TimeoutError, aiohttp.ClientResponseError)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Could not connect to {url} after {max_retries + 1} attempts"
            )
        except aiohttp.ClientResponseError as e:
            raise BaseError(
                f"Could not connect to {url} after {max_retries + 1} attempts. Server responded with error {e.status}"
            )

    async def do_http_connect(allow_redirect: bool):
        if not allow_redirect:
            raise BaseError(
                f"Server responded with a redirect for an invalid url: {url}"
            )
        async with aiohttp.ClientSession() as session:
            status, location = await http_connect_with_retry(session)
            if status not in (300, 301, 302, 303, 307, 308):
                raise BaseError(
                    f"Url '{url}' points to an HTTP location which is expected to redirect "
                    f"to a capnp server. However, the server did not respond with "
                    f"a valid redirect (returned status code is {status})"
                )
            if location is None:
                raise BaseError(
                    f"Cannot connect using url {url}. Server did not report the location of the capnp server."
                )
        return await do_connect(location, allow_redirect=False)

    async def do_connect(url: str, allow_redirect: bool):
        parsed_url = parse_url(url)
        if parsed_url.scheme == "tcp":
            return await do_tcp_connect(parsed_url)
        if parsed_url.scheme == "http":
            return await do_http_connect(allow_redirect)
        raise BadRequestError(
            f"Cannot connect using url {url}. Scheme {parsed_url.scheme} not supported"
        )

    return await do_connect(url, allow_redirect=True)


_comms.CapnpContext.connect_url = connect_url
