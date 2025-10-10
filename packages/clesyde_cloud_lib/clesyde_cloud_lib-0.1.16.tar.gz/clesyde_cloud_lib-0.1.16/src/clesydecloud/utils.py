"""Utilities."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from logging import Logger
import re
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def server_context_modern() -> ssl.SSLContext:
    """Return an SSL context following the Mozilla recommendations.

    TLS configuration follows the best-practice guidelines specified here:
    https://wiki.mozilla.org/Security/Server_Side_TLS
    Modern guidelines are followed.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)  # pylint: disable=no-member

    context.options |= (
        ssl.OP_NO_SSLv2
        | ssl.OP_NO_SSLv3
        | ssl.OP_NO_TLSv1
        | ssl.OP_NO_TLSv1_1
        | ssl.OP_CIPHER_SERVER_PREFERENCE
    )
    if hasattr(ssl, "OP_NO_COMPRESSION"):
        context.options |= ssl.OP_NO_COMPRESSION

    context.set_ciphers(
        "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:"
        "ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256"
    )

    return context


async def periodic_coroutine(
    interval_sec: float, coroutine, start_immediately=False, *args, **kwargs
):
    """Run a target periodically."""
    # loop until stop event is set
    if start_immediately:
        await coroutine(*args, **kwargs)

    while True:
        # wait an interval
        await asyncio.sleep(interval_sec)
        # await the target
        await coroutine(*args, **kwargs)


async def gather_callbacks(
    logger: Logger,
    name: str,
    callbacks: list[Callable[[], Awaitable[None]]],
) -> None:
    """Gather callbacks and log exceptions."""
    results = await asyncio.gather(*[cb() for cb in callbacks], return_exceptions=True)
    for result, callback in zip(results, callbacks, strict=False):
        if not isinstance(result, Exception):
            continue
        logger.error("Unexpected error in %s %s", name, callback, exc_info=result)


async def cancel_and_wait(
    task: asyncio.Task,
    msg: str | None = None,
    *,
    suppress_cancelled: bool = True,
) -> None:
    """Cancel `task` and wait until it finishes.

    Args:
        task: The task to cancel.
        msg: Optional cancellation message.
        suppress_cancelled: When True (default), swallow cancellation raised
            from the awaited task unless the *current* coroutine is itself
            being cancelled. Set to False when the caller wants the
            ``CancelledError`` to propagate.
    """
    if task.done():
        return
    task.cancel(msg)
    try:
        await task
    except asyncio.CancelledError:
        current_task = asyncio.current_task()
        if current_task is not None and current_task.cancelling():
            raise
        if suppress_cancelled:
            return
        raise
    else:
        raise RuntimeError("Cancelled task did not end with an exception")


@dataclass
class RegexEqual(str):  # noqa: SLOT000
    """Regex utility class."""

    string: str
    match: re.Match = None

    def __eq__(self, pattern):
        """Return True if there is a match."""
        self.match = re.search(pattern, self.string)
        return self.match is not None

    def __getitem__(self, group):
        """Return the matching item."""
        return self.match[group]

def retrieve_sn_from_pem(pem_data: bytes) -> str:
    certificate = x509.load_pem_x509_certificate(pem_data, default_backend())
    return str(certificate.serial_number)

def retrieve_sn_from_pem_file(pem_file: str) -> str:
    with open(pem_file, "rb") as pem_file:
        pem_data = pem_file.read()
        return retrieve_sn_from_pem(pem_data)
