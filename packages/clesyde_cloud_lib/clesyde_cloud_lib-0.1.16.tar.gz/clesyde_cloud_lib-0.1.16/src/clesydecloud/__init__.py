import asyncio  # noqa: D104
from collections.abc import Awaitable, Callable, Coroutine
import logging
from pathlib import Path
from typing import Any, Generic, TypeVar

from clesydecloud.client import ClesydeCloudClient
from clesydecloud.const import CONFIG_DIR
from clesydecloud.data import CloudConfig, DataError
from clesydecloud.iot import IoT
from clesydecloud.iot_message import IotMessage
from clesydecloud.provisioning import Provisioning
from clesydecloud.remote import RemoteAccess
from clesydecloud.utils import gather_callbacks
from clesydecloud.status import Status

_ClientT = TypeVar("_ClientT", bound=ClesydeCloudClient)
_LOGGER = logging.getLogger(__name__)


class InitializationError(Exception):
    """Exception raised when there was an error on cloud initialization."""

    def __init__(self, error: Any) -> None:
        """Initialize Error Message."""
        super().__init__("Error in Cloud")
        self.error = error


class ClesydeCloud(Generic[_ClientT]):
    """Implementation of Clesyde Cloud."""

    def __init__(
        self,
        client: _ClientT,
    ) -> None:
        """Init Cloud Client."""
        self.client = client

        self._on_initialized: list[Callable[[], Awaitable[None]]] = []
        self._on_start: list[Callable[[], Awaitable[None]]] = []
        self._on_stop: list[Callable[[], Awaitable[None]]] = []
        self._init_task: asyncio.Task | None = None

        self.config: CloudConfig | None = None

        self.started: bool | None = None

        self.iot_message = IotMessage(self)
        self.iot = IoT(self, iot_message=self.iot_message)
        self.provisioning = Provisioning(self)
        self.remote = RemoteAccess(self)

        # Set reference : for access to underline cloud function from ClesydeCloudClient instance
        self.client.cloud = self

        Path(self.path()).mkdir(parents=True, exist_ok=True)

    def path(self, *parts: Any) -> Path:
        """Get config path inside cloud dir.

        Async friendly.
        """
        return Path(self.client.base_path, CONFIG_DIR, *parts)

    def run_task(self, coro: Coroutine) -> asyncio.Task:
        """Schedule a task.

        Return a task.
        """
        return self.client.loop.create_task(coro)

    def run_executor(self, callback: Callable, *args: Any) -> asyncio.Future:
        """Run function inside executor.

        Return a awaitable object.
        """
        return self.client.loop.run_in_executor(None, callback, *args)

    def load_cloud_config(self) -> bool:
        """Load configuration from file."""
        try:
            _LOGGER.debug("Loading cloud config")
            self.config = CloudConfig.from_file(self.path())
        except DataError as de:
            _LOGGER.error("Error while loading local IoT config file")
            _LOGGER.error(de)
            return False

        if self.config is None:
            _LOGGER.error("Cloud config file is missing, cannot start cloud client")
            return False

        return True

    def cleanup_cloud_config(self) -> None:
        """Cleanup cloud config."""
        CloudConfig.cleanup(self.path())

    def register_on_initialized(
        self,
        on_initialized_cb: Callable[[], Awaitable[None]],
    ) -> None:
        """Register an async on_initialized callback.

        on_initialized callbacks are called after all on_start callbacks.
        """
        self._on_initialized.append(on_initialized_cb)

    def register_on_start(self, on_start_cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async on_start callback."""
        self._on_start.append(on_start_cb)

    def register_on_stop(self, on_stop_cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async on_stop callback."""
        self._on_stop.append(on_stop_cb)

    async def initialize(self) -> None:
        """Initialize cloud and start main async task."""
        config_loaded = await self.run_executor(self.load_cloud_config)
        if not config_loaded:
            self.started = False
            raise InitializationError("Could not load cloud config.")

        self._init_task = asyncio.create_task(self._finish_initialize())

    async def _finish_initialize(self):
        self.started = True
        await self._start()
        await gather_callbacks(_LOGGER, "on_initialized", self._on_initialized)
        self._init_task = None

    async def _start(self) -> None:
        """Start the cloud component."""
        await gather_callbacks(_LOGGER, "on_start", self._on_start)

    async def stop(self) -> None:
        """Stop the cloud component."""
        if self._init_task:
            self._init_task.cancel()
            self._init_task = None

        await gather_callbacks(_LOGGER, "on_stop", self._on_stop)

    def status(self) -> Status:
        """Return the cloud services status."""
        return Status(
            iot_connected=self.iot.is_connected(),
            remote_connected=self.remote.is_connected(),
        )
