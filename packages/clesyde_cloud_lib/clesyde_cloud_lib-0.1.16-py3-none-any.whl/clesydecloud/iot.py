"""Handle the communication with AWS IoT Core."""

from __future__ import annotations

import asyncio
from asyncio import CancelledError, Event, Queue
from collections.abc import Awaitable, Callable
import logging
import random
import ssl
from typing import TYPE_CHECKING, Final, Optional
from contextlib import suppress

from aiomqtt import Client, MqttError, ProtocolVersion, Will, MqttCodeError

from .iot_message import IotMessage
from .status import CloudService
from .utils import cancel_and_wait, gather_callbacks, server_context_modern

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT


payload_online: Final = '{"state":"ONLINE"}'
payload_offline: Final = '{"state":"OFFLINE"}'


class IoT(CloudService):
    """Manages the communication with IoT Core."""

    def __init__(self, cloud: ClesydeCloud[_ClientT], iot_message: IotMessage) -> None:
        """Initialize the IoT class."""
        self.cloud = cloud
        self._iot_message: IotMessage = iot_message

        self._client: Optional[Client] = None  # noqa: UP007
        self._publish_queue: Queue[tuple[str, int | float | str | bytes, int, bool]] | None = None
        self._is_connected: Event | None = None
        self._task: Optional[asyncio.Task | None] = None  # noqa: UP007
        self._listening_task: Optional[asyncio.Task | None] = None  # noqa: UP007

        self._on_connect: list[Callable[[], Awaitable[None]]] = []
        self._on_disconnect: list[Callable[[], Awaitable[None]]] = []
        self._con_retries: int = 0
        self._wait_for_con_retry_task: Optional[asyncio.Task | None] = None  # noqa: UP007
        self._context = None

        # Register start/stop
        self.cloud.register_on_start(self.start)
        self.cloud.register_on_stop(self.stop)

    def register_on_connect(self, on_connect_cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async on_connect callback."""
        self._on_connect.append(on_connect_cb)

    def register_on_disconnect(
        self,
        on_disconnect_cb: Callable[[], Awaitable[None]],
    ) -> None:
        """Register an async on_disconnect callback."""
        self._on_disconnect.append(on_disconnect_cb)

    async def start(self) -> None:
        """Start the connection."""
        self._context = await self._create_ssl_context()
        self._is_connected = Event()
        if self._task is None:
            _LOGGER.info("[start]: Creating IoT Task")
            self._task = self.cloud.run_task(self._mqtt_task())

    async def stop(self) -> None:
        """Stop the connection."""
        _LOGGER.debug("[stop]: Disconnecting")
        # Cancel listener and await it to avoid 'Task exception was never retrieved'
        if self._listening_task is not None:
            task = self._listening_task
            try:
                await cancel_and_wait(task, "iot.stop listening task")
            except CancelledError:
                pass
            finally:
                self._listening_task = None

        if self._wait_for_con_retry_task is not None:
            task = self._wait_for_con_retry_task
            try:
                await cancel_and_wait(task, "iot.stop wait retry")
            except CancelledError:
                pass
            finally:
                self._wait_for_con_retry_task = None

        # If the long-running mqtt task exists, cancel and swallow cancellation
        if self._task is not None:
            task = self._task
            try:
                await cancel_and_wait(task, "iot.stop main task")
            except CancelledError:
                pass
            finally:
                self._task = None

    async def _wait_before_connect(self) -> None:
        if self._con_retries == 0:
            self._wait_for_con_retry_task = None
            return

        # Exponential backoff with jitter
        base = 2 ** min(4, self._con_retries)  # 1,2,4,8,16
        seconds = base + random.randint(0, self._con_retries * 4)
        self._wait_for_con_retry_task = self.cloud.run_task(asyncio.sleep(seconds))
        _LOGGER.info("[_wait_before_connect]: Waiting %d seconds before retrying", seconds)
        await self._wait_for_con_retry_task
        self._wait_for_con_retry_task = None

    async def _listen_task(self) -> None:
        """Consume messages from aiomqtt and route them.

        Must catch MqttError/CancelledError to avoid unhandled task exceptions
        when the client disconnects, or we cancel the task.
        """
        if self._client is None:
            return

        _LOGGER.debug("[_listen_task]: Waiting for IoT Message")
        try:
            async for message in self._client.messages:
                try:
                    await self._iot_message.router(message)
                except Exception:
                    _LOGGER.exception("[_listen_task]: Error while routing IoT message")
        except CancelledError:
            _LOGGER.debug("[_listen_task]: Listen task cancelled")
            raise
        except MqttError as e:
            # Expected when the client disconnects during iteration
            _LOGGER.debug("[_listen_task]: Listen task ended due to MQTT disconnect: %s", e)
        except Exception:
            _LOGGER.exception("[_listen_task]: Unexpected error in listen task")

    async def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with acme certificate."""
        context = server_context_modern()

        await self.cloud.run_executor(
            context.load_cert_chain,
            self.cloud.config.iot_cert_file(self.cloud),
            self.cloud.config.iot_key_file(self.cloud),
        )
        await self.cloud.run_executor(
            context.load_verify_locations,
            self.cloud.config.iot_ca_file(self.cloud),
        )
        return context

    async def _mqtt_task(self):
        self._is_connected = Event()
        shutdown = False
        self._con_retries = 0
        self._publish_queue = Queue()

        while not shutdown:
            try:
                await self._wait_before_connect()
                if self._con_retries > 0:
                    _LOGGER.info("[_mqtt_task]: Connecting (retry %d)", self._con_retries)
                else:
                    _LOGGER.info("[_mqtt_task]: Connecting")
                self._con_retries += 1

                try:
                    last_will = Will(
                        topic=self._iot_message.status_topic, payload=payload_offline
                    )

                    self._client = Client(
                        hostname=self.cloud.config.iot_endpoint,
                        port=8883,
                        identifier=self.cloud.config.iot_thing_name,
                        protocol=ProtocolVersion.V5,
                        transport="tcp",
                        will=last_will,
                        tls_context=self._context,
                    )

                    async with self._client:
                        _LOGGER.debug("[_mqtt_task]: Connected successfully!")
                        self._con_retries = 0
                        self._is_connected.set()

                        _LOGGER.debug("[_mqtt_task]: Topics subscription")
                        subscription_result = [
                            (await self._client.subscribe(topic), topic)
                            for topic in self._iot_message.subscriptions()
                        ]
                        _LOGGER.debug(subscription_result)
                        _LOGGER.debug("[_mqtt_task]: Subscribed to topics")

                        # Start the listening task (now robust to disconnects)
                        self._listening_task = self.cloud.run_task(self._listen_task())

                        if self._on_connect:
                            await gather_callbacks(_LOGGER, "on_connect", self._on_connect)

                        try:
                            # signal that we are online
                            _LOGGER.debug("[_mqtt_task]: Sending online status")
                            await self._client.publish(
                                self._iot_message.status_topic, payload_online, 0, False
                            )

                            while True:
                                topic, value, qos, retain = await self._publish_queue.get()
                                try:
                                    await self._client.publish(topic, value, qos, retain)
                                except MqttCodeError as e:
                                    self._publish_queue.put_nowait((topic, value, qos, retain))
                                    _LOGGER.debug(
                                        "[_mqtt_task]: Error while publishing message, keep it in the queue"
                                    )
                                    _LOGGER.exception(e)
                                    _LOGGER.debug(
                                        "[_mqtt_task]: Current queue size: %s",
                                        self._publish_queue.qsize(),
                                    )
                                    raise
                                finally:
                                    self._publish_queue.task_done()

                        except CancelledError as error:
                            _LOGGER.debug(
                                "[_mqtt_task]: CancelledError, shutting down mqtt task (%s)",
                                error,
                            )
                            shutdown = True
                            with suppress(Exception):
                                await self._client.publish(
                                    self._iot_message.status_topic,
                                    payload_offline,
                                    0,
                                    False,
                                )
                            raise

                except MqttError as e:
                    _LOGGER.debug("[_mqtt_task]: Mqtt error during connect/loop")
                    _LOGGER.error(e)
                except OSError as ex:
                    _LOGGER.debug("[_mqtt_task]: OSError during connect/loop")
                    _LOGGER.error(ex)

            except CancelledError as error:
                _LOGGER.debug(
                    "[_mqtt_task]: Cancelled while waiting before connect; shutting down mqtt task (%s)",
                    error,
                )
                shutdown = True
                raise

            finally:
                # Ensure the listen task is stopped cleanly before looping/reconnecting
                if self._listening_task is not None:
                    task = self._listening_task
                    try:
                        await cancel_and_wait(task, "iot._mqtt_task listen cleanup")
                    except CancelledError:
                        pass
                    finally:
                        self._listening_task = None

                if shutdown:
                    self._publish_queue = None

                if self._is_connected is not None:
                    self._is_connected.clear()

                if self._on_disconnect:
                    await gather_callbacks(_LOGGER, "on_disconnect", self._on_disconnect)

                # reference clean-up
                self._client = None

            if not shutdown:
                _LOGGER.debug("[_mqtt_task]: Looping _mqtt_task (will retry connect)")

        _LOGGER.debug("[_mqtt_task]: Leaving _mqtt_task")

    def publish(self, topic: str, value: float | str | bytes, qos: int, retain: bool):
        """Publish a message."""
        if self._publish_queue is not None:
            self._publish_queue.put_nowait((topic, value, qos, retain))
        else:
            _LOGGER.debug("[publish]: Dropping publish, client not connected: %s", topic)

    def is_connected(self):
        return self._is_connected is not None and self._is_connected.is_set()
