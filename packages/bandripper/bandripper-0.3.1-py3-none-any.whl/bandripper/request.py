from ssl import SSLContext
from typing import Any

import gruel
from requests.adapters import (
    DEFAULT_POOLBLOCK,
    DEFAULT_POOLSIZE,
    DEFAULT_RETRIES,
    HTTPAdapter,
)
from urllib3.util import create_urllib3_context

""" 
This is neccessary to get around bandcamp returning 403 errors due to bandcamp not seeing the additional cipher suites.

See: https://github.com/urllib3/urllib3/issues/3439#issuecomment-2306400349

"""


class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context: SSLContext) -> None:
        self.ssl_context: SSLContext = ssl_context
        super().__init__(
            DEFAULT_POOLSIZE, DEFAULT_POOLSIZE, DEFAULT_RETRIES, DEFAULT_POOLBLOCK
        )

    def init_poolmanager(
        self,
        connections: int,
        maxsize: int,
        block: bool = DEFAULT_POOLBLOCK,
        **pool_kwargs: Any,
    ) -> None:
        pool_kwargs["ssl_context"] = self.ssl_context
        super().init_poolmanager(  # type: ignore
            connections, maxsize, block, **pool_kwargs
        )

    def proxy_manager_for(self, proxy: str, **proxy_kwargs: Any) -> str:
        proxy_kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(proxy, **proxy_kwargs)  # type: ignore


def get_session() -> gruel.Session:
    """
    Get a `gruel.Session` object that has the require cipher added to satisfy bandcamp.

    Returns
    -------
    gruel.Session
        A session to make bandcamp requests with.
    """
    ctx: SSLContext = create_urllib3_context()
    ctx.load_default_certs()
    DEFAULT_CIPHERS: str = ":".join(
        [
            "ECDHE+AESGCM",
            "ECDHE+CHACHA20",
            "DHE+AESGCM",
            "DHE+CHACHA20",
            "ECDH+AESGCM",
            "DH+AESGCM",
            "ECDH+AES",
            "DH+AES",
            "RSA+AESGCM",
            "RSA+AES",
            "!aNULL",
            "!eNULL",
            "!MD5",
            "!DSS",
            "!AESCCM",
        ]
    )
    ctx.set_ciphers(DEFAULT_CIPHERS)
    session = gruel.Session()
    session.mount("https://", SSLAdapter(ssl_context=ctx))
    return session
