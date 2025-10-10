from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True, slots=True)
class Status:
    iot_connected: bool
    remote_connected: bool


class CloudService(ABC):
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Return the cloud service status."""




