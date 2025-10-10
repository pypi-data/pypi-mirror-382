"""IOT Message class."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
import logging
import re
from typing import TYPE_CHECKING

from aiomqtt import Message

from .const import (
    IOT_PLATFORM_TOPIC,
    IOT_THING_D2P_PREFIX,
    IOT_THING_SHADOW_TOPIC_PREFIX,
    IOT_THING_TOPIC_STATUS_SUFFIX,
)
from .iot_shadow import IotShadowUpdate

from .utils import RegexEqual

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT


def platform2device_topic_prefix(sn: str) -> str:
    """Get the topic prefix."""
    return f"{IOT_THING_D2P_PREFIX}/{sn}"


def platform2device_action_pattern(sn: str) -> str:
    """Get the device action pattern."""
    prefix_escaped = re.escape(f"{IOT_THING_D2P_PREFIX}/{sn}")
    return f"^{prefix_escaped}/(?P<action_name>[a-zA-Z0-9_-]+)/res$"


def shadow_name_topic_prefix(sn: str, shadow_name: str) -> str:
    """Get the prefix of shadow name topic."""
    return f"{IOT_THING_SHADOW_TOPIC_PREFIX}/{sn}/shadow/name/{shadow_name}"


def named_shadow_topic_prefix_pattern(sn: str) -> str:
    """Get the pattern for the shadow topic name."""
    prefix_escaped = re.escape(f"{IOT_THING_SHADOW_TOPIC_PREFIX}/{sn}/shadow/name")
    return f"^{prefix_escaped}/(?P<shadow_name>[a-zA-Z0-9_-]+)/(?P<shadow_command>.*)$"


class IotMessage:
    """The actual IoT Message class."""

    def __init__(
        self,
        cloud: ClesydeCloud[_ClientT],
    ) -> None:
        """Initialize an IoT message."""
        self.cloud = cloud
        self._named_shadow_topic_pattern = named_shadow_topic_prefix_pattern(
            self.cloud.client.device_sn
        )
        self._p2d_action_pattern = platform2device_action_pattern(
            self.cloud.client.device_sn
        )
        self._on_message: list[Callable[[Message], Awaitable[None]]] = []

    @property
    def status_topic(self) -> str:
        """Get the status topic."""
        return f"{IOT_THING_D2P_PREFIX}/{self.cloud.client.device_sn}/{IOT_THING_TOPIC_STATUS_SUFFIX}"

    def subscriptions(self) -> list[str]:
        """Get the subscriptions."""
        thing_config_shadow_prefix = shadow_name_topic_prefix(
            self.cloud.client.device_sn, "config"
        )
        thing_platform2device_topic_prefix = platform2device_topic_prefix(
            self.cloud.client.device_sn
        )
        return [
            IOT_PLATFORM_TOPIC,
            f"{thing_platform2device_topic_prefix}/+/res",
            f"{thing_config_shadow_prefix}/+/accepted",
            f"{thing_config_shadow_prefix}/+/rejected",
            f"{thing_config_shadow_prefix}/+/delta",
            f"{thing_config_shadow_prefix}/+/documents",
        ]

    def on_named_shadow_message(self, name: str, command: str, payload: str) -> None:
        """Print a debug log on callback for shadow message."""
        _LOGGER.debug("Shadow message")

        _LOGGER.debug(name)
        _LOGGER.debug(command)
        _LOGGER.debug(payload)

        if name == "config" and command == "update/delta":
            _LOGGER.debug("shadow config update message")

            try:
                payload_obj = json.loads(payload)
                if "state" in payload_obj:
                    shadow = IotShadowUpdate.from_dict(payload_obj["state"])
                    updates = shadow.delta.extract_existing_keys()

                ## test relevant update to manage :

                # Remote Cert SN : check for cert rotation
                if "remote_cert_sn" in updates:
                    self.cloud.remote.on_request_cert_refresh(shadow.delta.remote_cert_sn)

            except Exception as e:
                _LOGGER.error("Error while parsing shadow update message")
                _LOGGER.exception(e)


    async def on_p2d_action(self, action: str, payload: str) -> None:
        """Handle Platform 2 Device action."""
        if action == "remotetoken":
            _LOGGER.debug("remote token message received")
            await self.cloud.remote.on_new_snitun_token(message_payload=payload)
            return
        if action == "remotecr":
            _LOGGER.debug("Remote cr message")
            await self.cloud.remote.on_received_cert_refresh(message_payload=payload)
            return
        else:
            _LOGGER.debug("Unknown Action response:")
            _LOGGER.debug(action)
            _LOGGER.debug(payload)

    async def router(self, message: Message):
        """Route incoming IoT message to the relevant method"""
        try:
            match RegexEqual(message.topic.value):
                case self._named_shadow_topic_pattern as capture:
                    self.on_named_shadow_message(
                        capture["shadow_name"],
                        capture["shadow_command"],
                        message.payload,
                    )
                case self._p2d_action_pattern as capture:
                    await self.on_p2d_action(capture["action_name"], message.payload)
                case _:
                    _LOGGER.warning("Unmanaged topic: %s", message.topic)
                    _LOGGER.info(message.payload)
        except OSError as e:
            _LOGGER.error("Error while parsing IoT message (topic: %s)", message.topic)
            _LOGGER.error(message.payload)
            _LOGGER.error(e)
