"""Data utility helper."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any
import shutil

from .const import (
    CONFIG_FILE,
    IOT_CA_FILE,
    IOT_CERT_FILE,
    IOT_KEY_FILE,
    REMOTE_CERT_FILE,
    REMOTE_KEY_FILE,
)

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT


class DataError(Exception):
    """Raise for any serialization or deserialization errors."""

    def __init__(self, message: str) -> None:
        """Initialize data Error class."""

        super().__init__(message)


class EnhancedJSONEncoder(json.JSONEncoder):
    """Enhanced JSON Encoder."""

    def default(self, o):
        """Return the best encoder."""

        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclass(frozen=True)
class CloudConfig:
    """Manages the cloud config."""

    iot_thing_name: str
    iot_endpoint: str
    remote_endpoint: str
    access_point: str

    def to_json(self) -> str:
        """Create a JSON string from config."""
        return json.dumps(self, cls=EnhancedJSONEncoder)

    @staticmethod
    def from_file(base_path: Path) -> Any | None:
        """Load the configuration of the cloud from a JSON file."""
        config_file_path = base_path / CONFIG_FILE
        try:
            if config_file_path.is_file():
                with config_file_path.open(encoding="utf-8") as infile:
                    json_str = infile.read()
                    json_obj = json.loads(json_str)
                    if json_obj is not None:
                        return CloudConfig(**json_obj)
                    return None
            else:
                return None
        except OSError as e:
            raise DataError(
                f"Error while loading config from file {config_file_path}"
            ) from e

    @staticmethod
    def _persist(base_path: Path, file_name: str, content: str) -> None:
        # check if the base path exists, if not create it
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
        file_path = base_path / file_name
        with file_path.open(mode="w", encoding="utf-8") as outfile:
            outfile.write(content)
        file_path.chmod(0o600)

    @staticmethod
    def persist_from_api_thing(thing: dict[str, str], base_path: Path) -> CloudConfig:
        """Persist the information gathered from Thing API."""
        try:
            iot = thing["iot"]

            iot_cert_pem = iot["certificates"]["device_certificate"]
            iot_ca_pem = iot["certificates"]["root_ca"]

            iot_key_pair = iot["keyPair"]
            iot_pkey = iot_key_pair["privateKey"]

            remote = thing["remote"]
            remote_pkey = remote["pkey"]
            remote_cert = remote["cert"]

            config = CloudConfig(
                iot_endpoint=iot["endpoint"],
                iot_thing_name=iot["thing_name"],
                remote_endpoint=remote["endpoint"],
                access_point=remote["access_point"],
            )

            CloudConfig._persist(base_path, CONFIG_FILE, config.to_json())
            CloudConfig._persist(base_path, IOT_CA_FILE, iot_ca_pem)
            CloudConfig._persist(base_path, IOT_CERT_FILE, iot_cert_pem)
            CloudConfig._persist(base_path, IOT_KEY_FILE, iot_pkey)

            CloudConfig._persist(base_path, REMOTE_CERT_FILE, remote_cert)
            CloudConfig._persist(base_path, REMOTE_KEY_FILE, remote_pkey)
        except KeyError as e:
            raise DataError(f"Missing thing attribute: {e}") from e
        else:
            return config

    @staticmethod
    def cleanup(base_path: Path) -> None:
        """Clean the Cloud config folder and remove any trace."""
        shutil.rmtree(base_path)

    @staticmethod
    def iot_ca_file(cloud: ClesydeCloud[_ClientT]) -> str:
        """Certificate Authority file for IoT connection."""
        return str(cloud.path(IOT_CA_FILE))

    @staticmethod
    def iot_cert_file(cloud: ClesydeCloud[_ClientT]) -> str:
        """Certificate file for IoT connection."""
        return str(cloud.path(IOT_CERT_FILE))

    @staticmethod
    def iot_key_file(cloud: ClesydeCloud[_ClientT]) -> str:
        """Certificate key file for IoT connection."""
        return str(cloud.path(IOT_KEY_FILE))

    @staticmethod
    def remote_cert_file(cloud: ClesydeCloud[_ClientT]) -> str:
        """Certificate file for SniTun connection."""
        return str(cloud.path(REMOTE_CERT_FILE))

    @staticmethod
    def remote_key_file(cloud: ClesydeCloud[_ClientT]) -> str:
        """Certificate key file for SniTun Connection."""
        return str(cloud.path(REMOTE_KEY_FILE))

    @staticmethod
    def update_remote_cert(base_path: Path, cert_content:str, pkey_content:str):
        CloudConfig._persist(base_path, REMOTE_CERT_FILE, cert_content)
        CloudConfig._persist(base_path, REMOTE_KEY_FILE, pkey_content)
