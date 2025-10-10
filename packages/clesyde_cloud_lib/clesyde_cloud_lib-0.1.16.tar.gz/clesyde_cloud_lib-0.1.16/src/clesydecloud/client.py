"""Access to ClesydeCloudClient instance in HA."""

from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import TYPE_CHECKING

from aiohttp import web

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud


class ClesydeCloudClient(ABC):
    """Provide access to underline cloud function from ClesydeCloudClient instance."""

    cloud: ClesydeCloud

    """
    All methods below are called by the ClesydeCloud instance to either :
        - retrieve context information (where the ClesydeCloud instance is running)
        - send a request to the running context (ie. the device)
    """

    @property
    @abstractmethod
    def device_sn(self) -> str:
        """Return the device serial number."""

    @property
    @abstractmethod
    def base_path(self) -> Path:
        """Return path to base dir."""

    @property
    @abstractmethod
    def loop(self) -> AbstractEventLoop:
        """Return client loop."""

    @property
    @abstractmethod
    def api_base_url(self) -> str:
        """Return ClesydeCloud api url."""

    #    @property
    #    @abstractmethod
    #    def websession(self) -> aiohttp.ClientSession:
    #        """Return client session for aiohttp."""

    @property
    @abstractmethod
    def aiohttp_runner(self) -> web.AppRunner | None:
        """Return client webinterface aiohttp application."""
