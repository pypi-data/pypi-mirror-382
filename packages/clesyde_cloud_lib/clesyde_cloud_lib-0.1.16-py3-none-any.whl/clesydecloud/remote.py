"""Manage remote UI connections."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
import random
import ssl
from typing import TYPE_CHECKING

import async_timeout  # noqa: TID251
from snitun.exceptions import SniTunConnectionError
from snitun.utils.aes import generate_aes_keyset
from snitun.utils.aiohttp_client import SniTunClientAioHttp

from .data import CloudConfig
from .status import CloudService
from .utils import (
    cancel_and_wait,
    gather_callbacks,
    periodic_coroutine,
    retrieve_sn_from_pem_file,
    server_context_modern,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT

# interval of seconds between each snitun refresh task restart
_REFRESH_SNITUN_TOKEN_INTERVAL_SEC = 300
# number of secs to wait for IoT response for token refresh, before asking again
_SNITUN_TOKEN_REFRESH_TIMEOUT_SEC = 60
# Remaining minutes before expiration threshold to trigger refresh
_SNITUN_TOKEN_EXPIRATION_LIMIT_MINS = 15

# Remote snitun server TCP port
_SNITUN_REMOTE_TCP_PORT = 443


@dataclass
class SniTunTokenPayload:
    """Encapsulate snitun token information."""

    valid: int
    throttling: int
    token: str

@dataclass
class CertRefreshPayload:
    cert:str
    pkey:str


class RemoteAccess(CloudService):
    """Manages the remote connection using SniTun."""

    def __init__(self, cloud: ClesydeCloud[_ClientT]) -> None:
        """Initialize RemoteAccess class. Register cloud hooks."""
        self.cloud = cloud

        # Task to monitor snitun connection and to start reconnection on disconnect
        self.remote_client_reconnect_task: asyncio.Task | None = None
        # Task to check snitun token, and trigger its refresh depending on specified conditions
        self.periodic_snitun_token_refresh_task: asyncio.Task | None = None
        self._reconnect_guard_stop: asyncio.Event = asyncio.Event()

        self.is_iot_connected: bool = False
        self._snitun_token_payload: SniTunTokenPayload | None = None
        self.snitun_client: SniTunClientAioHttp | None = None
        self.is_refreshing_snitun_token: bool = False

        self._aes_key: bytes | None = None
        self._aes_iv: bytes | None = None

        self._on_connect: list[Callable[[], Awaitable[None]]] = []
        self._on_disconnect: list[Callable[[], Awaitable[None]]] = []

        self.cloud.iot.register_on_connect(self.on_iot_connected)
        self.cloud.iot.register_on_disconnect(self.on_iot_disconnected)
        self.cloud.register_on_stop(self.on_stop)

    def register_on_connect(self, on_connect_cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async on_connect callback."""
        self._on_connect.append(on_connect_cb)

    def register_on_disconnect(
        self,
        on_disconnect_cb: Callable[[], Awaitable[None]],
    ) -> None:
        """Register an async on_disconnect callback."""
        self._on_disconnect.append(on_disconnect_cb)

    def _token_valid_to_mins(self) -> float:
        """Remaining time in minutes before snitun token expiration.

        :return: float
        """
        if self._snitun_token_payload is not None:
            converted_valid = datetime.fromtimestamp(
                self._snitun_token_payload.valid, UTC
            )
            current_time_utc = datetime.now(UTC)
            return (converted_valid - current_time_utc).total_seconds() / 60
        # else
        return 0

    def _is_token_expired(self) -> bool:
        """Snitun token expiration is lower than the defined threshold _SNITUN_TOKEN_EXPIRATION_LIMIT_MINS.

        :return: bool
        """
        delta_min = self._token_valid_to_mins()
        _LOGGER.debug("[_is_token_expired]: SNITUN Token expire in %s mins", delta_min)
        if delta_min < _SNITUN_TOKEN_EXPIRATION_LIMIT_MINS:
            return True
        # else
        return False

    async def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with acme certificate."""
        context = server_context_modern()

        # We can not get here without this being set, but mypy does not know that.
        # assert self._acme is not None
        await self.cloud.run_executor(
            context.load_cert_chain,
            self.cloud.config.remote_cert_file(self.cloud),
            self.cloud.config.remote_key_file(self.cloud),
        )
        return context

    async def on_iot_connected(self):
        """Prepare for reconnection. Callback called on iot connected."""
        _LOGGER.debug("[on_iot_connected]: Start")
        self.is_iot_connected = True
        if self.periodic_snitun_token_refresh_task is None:
            _LOGGER.debug("[on_iot_connected]: Recreating periodic_snitun_token_refresh_task")
            self.periodic_snitun_token_refresh_task = self.cloud.run_task(
                # no re-entrance, has the periodic_coroutine wait for coroutine to end,
                # before starting a new cycle
                periodic_coroutine(
                    _REFRESH_SNITUN_TOKEN_INTERVAL_SEC,
                    self._refresh_snitun_token,
                    start_immediately=True,
                )
            )
        _LOGGER.debug("[on_iot_connected]: End")

    async def on_iot_disconnected(self):
        """Refresh the token if needed. Callback called when iot is disconnected."""
        _LOGGER.debug("[on_iot_disconnected]: Start")
        self.is_iot_connected = False
        if self.periodic_snitun_token_refresh_task is not None:
            _LOGGER.debug("[on_iot_disconnected]: Canceling periodic_snitun_token_refresh_task")
            task = self.periodic_snitun_token_refresh_task
            try:
                await cancel_and_wait(task, "on_iot_disconnected called")
            except asyncio.CancelledError:
                pass
            finally:
                self.periodic_snitun_token_refresh_task = None
        _LOGGER.debug("[on_iot_disconnected]: End")

    async def on_stop(self):
        """Stop the snitun client. Callback called when cloud stack is stopped."""
        await self._stop_snitun_client()

    async def _refresh_snitun_token(self):
        """Refresh Snitun token."""
        _LOGGER.debug("[_refresh_snitun_token]: Start - Checking for expired snitun token")
        token_has_expired = self._is_token_expired()
        if (
            not self.is_refreshing_snitun_token
            and self.is_iot_connected
            and (self._snitun_token_payload is None or token_has_expired)
        ):
            if token_has_expired:
                _LOGGER.debug("[_refresh_snitun_token]: Missing or expired snitun token, refreshing it")
            self.is_refreshing_snitun_token = True
            aes_key, aes_iv = generate_aes_keyset()
            self._aes_key = aes_key
            self._aes_iv = aes_iv
            # important: snitun expect keyset value (bytes) to be encoded
            # as hexadecimal string in the fernet token
            payload: str = json.dumps(
                {"aesKey": self._aes_key.hex(), "aesIv": self._aes_iv.hex()}
            )
            _LOGGER.debug("[_refresh_snitun_token]: sending new token request")
            remote_token_topic = f"c/d/{self.cloud.client.device_sn}/remotetoken/req"
            self.cloud.iot.publish(remote_token_topic, payload, 0, False)

            await asyncio.sleep(_SNITUN_TOKEN_REFRESH_TIMEOUT_SEC)
            self.is_refreshing_snitun_token = False
        _LOGGER.debug("[_refresh_snitun_token]: End")

    async def on_new_snitun_token(self, message_payload: str):
        """Process the new snitun token."""

        _LOGGER.debug("[on_new_snitun_token]: Received new snitun token")
        if self.is_refreshing_snitun_token:
            self.is_refreshing_snitun_token = False
            try:
                payload = json.loads(message_payload)
                self._snitun_token_payload = SniTunTokenPayload(
                    valid=payload["valid"],
                    throttling=payload["throttling"],
                    token=payload["token"],
                )
                _LOGGER.debug(
                    "[on_new_snitun_token]: New snitun token received, valid for %.2f minutes",
                    self._token_valid_to_mins(),
                )

            except json.JSONDecodeError as e:
                _LOGGER.error("[on_new_snitun_token]: Received invalid snitun token (%s)", e)
                self._snitun_token_payload = None
            except OSError as e:
                _LOGGER.error("[on_new_snitun_token]: Unknown error with new snitun token (%s)", e)
                self._snitun_token_payload = None

            if self._snitun_token_payload is not None:
                _LOGGER.info("[on_new_snitun_token]: Start or recycle Snitun client")
                await self._recycle_snitun_client()

        else:
            _LOGGER.debug(
                "[on_new_snitun_token]: New token ignored, as it seems to be from an old/previous request"
            )

    async def _recycle_snitun_client(self) -> None:
        _LOGGER.debug("[_recycle_snitun_client]: Start")
        await self._stop_snitun_client()
        await self._start_snitun_client()
        _LOGGER.debug("[_recycle_snitun_client]: End")

    async def _stop_snitun_client(self):
        _LOGGER.debug("[_stop_snitun_client]: Start")
        if self.remote_client_reconnect_task is not None:
            task = self.remote_client_reconnect_task
            self._reconnect_guard_stop.set()
            if not task.done():
                try:
                    await asyncio.shield(task)
                except asyncio.CancelledError:
                    if not self._reconnect_guard_stop.is_set():
                        raise
            self.remote_client_reconnect_task = None
            self._reconnect_guard_stop.clear()

        if self.snitun_client is not None and self.snitun_client.is_connected:
            await self.snitun_client.disconnect()
        if self._on_disconnect:
            await gather_callbacks(_LOGGER, "on_disconnect", self._on_disconnect)
        _LOGGER.debug("[_stop_snitun_client]: End")

    async def _start_snitun_client(self):
        context = await self._create_ssl_context()
        self.snitun_client = SniTunClientAioHttp(
            self.cloud.client.aiohttp_runner,
            context,
            snitun_server=self.cloud.config.remote_endpoint,
            snitun_port=_SNITUN_REMOTE_TCP_PORT,
        )

        # Important : callback set must be the handler not the coroutine
        await self.snitun_client.start(False, self._recycle_snitun_client)
        self.cloud.run_task(self._connect_snitun_client())

    async def _connect_snitun_client(self):
        if self.snitun_client is not None and not self.snitun_client.is_connected:
            _LOGGER.debug("[_connect_snitun_client]: snitun connecting")
            try:
                async with async_timeout.timeout(30):
                    await self.snitun_client.connect(
                        fernet_key=self._snitun_token_payload.token.encode(),
                        aes_key=self._aes_key,
                        aes_iv=self._aes_iv,
                        throttling=self._snitun_token_payload.throttling,
                    )
                    if self._on_connect:
                        await gather_callbacks(_LOGGER, "on_connect", self._on_connect)
                    _LOGGER.info("[_connect_snitun_client]: Snitun connected")
                    _LOGGER.info(
                        "[_connect_snitun_client]: Device available here: https://%s:%s",
                        self.cloud.config.access_point,
                        _SNITUN_REMOTE_TCP_PORT,
                    )
            except TimeoutError:
                _LOGGER.error("[_connect_snitun_client]: Timeout connecting to snitun server")
            except SniTunConnectionError as err:
                _LOGGER.error("[_connect_snitun_client]: Failed to connect to snitun server (%s)", err)
            finally:
                # start retry reconnection task if :
                # - no snitun client,
                # - no reconnect task,
                # - and snitun token NOT expired
                if (
                    self.snitun_client
                    and not self.remote_client_reconnect_task
                    and not self._is_token_expired()
                ):
                    _LOGGER.debug("[_connect_snitun_client]: creating automatic reconnect task")
                    self._reconnect_guard_stop.clear()
                    self.remote_client_reconnect_task = self.cloud.run_task(self._reconnect_snitun_client())

                # No guard is active while the token is expired: restart the guard and request a refresh
                elif (
                    self.snitun_client
                    and not self.remote_client_reconnect_task
                    and self._is_token_expired()
                ):
                    _LOGGER.debug(
                        "[_connect_snitun_client]: token expired without reconnect guard; restarting guard and requesting refresh"
                    )
                    if self.is_iot_connected and not self.is_refreshing_snitun_token:
                        self.cloud.run_task(self._refresh_snitun_token())
                    self._reconnect_guard_stop.clear()
                    self.remote_client_reconnect_task = self.cloud.run_task(self._reconnect_snitun_client())

                # Disconnect if the instance is mark as insecure (token expired) and we're in reconnect mode
                elif self.remote_client_reconnect_task and self._is_token_expired():
                    _LOGGER.debug("[_connect_snitun_client]: connection error, and token expired, recycle server")
                    self.cloud.run_task(self._recycle_snitun_client())

    async def _reconnect_snitun_client(self):
        """Automatically reconnect after disconnect."""
        try:
            while not self._reconnect_guard_stop.is_set():
                if self.snitun_client is not None and self.snitun_client.is_connected:
                    wait_for_disconnect = self.snitun_client.wait()
                    wait_for_stop = asyncio.create_task(self._reconnect_guard_stop.wait())

                    done, _ = await asyncio.wait(
                        {wait_for_disconnect, wait_for_stop},
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    if wait_for_stop in done and self._reconnect_guard_stop.is_set():
                        wait_for_disconnect.cancel()
                        await asyncio.gather(wait_for_disconnect, return_exceptions=True)
                        await asyncio.gather(wait_for_stop, return_exceptions=True)
                        break

                    wait_for_stop.cancel()
                    await asyncio.gather(wait_for_stop, return_exceptions=True)

                    await asyncio.gather(wait_for_disconnect, return_exceptions=True)

                    _LOGGER.debug("[_reconnect_snitun_client]: Snitun disconnected, will try to reconnect")

                if self._reconnect_guard_stop.is_set():
                    break

                wait_for_retry = random.randint(1, 15)
                _LOGGER.debug(
                    "[_reconnect_snitun_client]: Snitun client wait %s seconds before retrying connection",
                    wait_for_retry,
                )
                try:
                    await asyncio.wait_for(
                        self._reconnect_guard_stop.wait(),
                        timeout=wait_for_retry,
                    )
                    break
                except asyncio.TimeoutError:
                    pass

                await self._connect_snitun_client()
        except asyncio.CancelledError as error:
            _LOGGER.debug(
                "[_reconnect_snitun_client]: CancelledError, ending remote access (%s)",
                error,
            )
            if not self._reconnect_guard_stop.is_set():
                raise
        finally:
            _LOGGER.debug("[_reconnect_snitun_client]: Close remote client reconnect guard")
            self.remote_client_reconnect_task = None

    def is_connected(self) -> bool:
        return self.snitun_client is not None and self.snitun_client.is_connected

    def on_request_cert_refresh(self, serial_number: str):
        _LOGGER.debug("[on_request_cert_refresh]: Received cert rotation message")
        cert_file = self.cloud.config.remote_cert_file(self.cloud)
        current_sn = retrieve_sn_from_pem_file(cert_file)
        if serial_number != current_sn:
            _LOGGER.debug("[on_request_cert_refresh]: Must update certificate file")

            payload: str = json.dumps({"remoteCertSn": serial_number})
            _LOGGER.debug("[on_request_cert_refresh]: sending remote cert retrieval request")
            remote_cert_refresh_topic = f"c/d/{self.cloud.client.device_sn}/remotecr/req"
            self.cloud.iot.publish(remote_cert_refresh_topic, payload, 0, False)

        else:
            _LOGGER.debug("[on_request_cert_refresh]: Same certificate file, nothing to do")

    async def on_received_cert_refresh(self, message_payload:str):
        try:
            _LOGGER.debug("[on_received_cert_refresh]: Received cert rotation message")
            payload = json.loads(message_payload)
            cert_refresh = CertRefreshPayload(
                cert=payload["cert"],
                pkey=payload["pkey"],
            )
            _LOGGER.debug("[on_received_cert_refresh]: Saving new certificate")
            await self.cloud.run_executor(
                CloudConfig.update_remote_cert,
                self.cloud.path(),
                cert_refresh.cert,
                cert_refresh.pkey,
            )
            _LOGGER.debug("[on_received_cert_refresh]: Restarting remote client")
            await self._recycle_snitun_client()

        except json.JSONDecodeError as e:
            _LOGGER.error("[on_received_cert_refresh]: Received invalid cert refresh message (%s)", e)
        except OSError as e:
            _LOGGER.error("[on_received_cert_refresh]: ``Unknown error with cert refresh message (%s)", e)
