"""Manage IoT certs updates."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
import random
import ssl
import aiohttp
from typing import TYPE_CHECKING

from .data import CloudConfig, DataError
from .utils import gather_callbacks, periodic_coroutine, server_context_modern

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT

class IoTCerts:
    """Manages the remote connection using SniTun."""

    def __init__(self, cloud: ClesydeCloud[_ClientT]) -> None:
        """Initialize RemoteAccess class. Register cloud hooks."""
        self.cloud = cloud

    async def _start_rotate_certificate(self) -> None:
        try:
            cloud_config = await self.cloud.run_executor(
                CloudConfig.from_file, self.cloud.path()
            )
        except DataError as de:
            _LOGGER.error("Error while loading local cloud config file")
            _LOGGER.error(de)
            return

        if cloud_config is None:
            _LOGGER.info("Stopping here, provisioning configuration was not found")
            return


