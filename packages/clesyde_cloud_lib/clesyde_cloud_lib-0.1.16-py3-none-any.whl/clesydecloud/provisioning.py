"""Provision a device from the cloud."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import aiohttp

from .const import IOT_PROVISIONING_API_PATH
from .data import CloudConfig, DataError

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT


class ProvisioningError(Exception):
    """Exception raised for errors in the provisioning process."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class Provisioning:
    """Helper class to provision a device."""

    def __init__(self, cloud: ClesydeCloud[_ClientT]) -> None:
        """Init the provisioner."""
        self.cloud = cloud

    async def start_provisioning(self, provisioning_key: str):
        """Start provisioning the device."""
        # 1) Check of any existing config files
        try:
            cloud_config = await self.cloud.run_executor(
                CloudConfig.from_file, self.cloud.path()
            )
        except DataError as de:
            _LOGGER.error("Error while loading local cloud config file")
            _LOGGER.error(de)
            return

        if cloud_config is not None:
            _LOGGER.info("Skipping provisioning because config files already exist")
            return

        # 2) Start of provisioning
        _LOGGER.info(
            "No valid configuration found, calling provisioning API to retrieve config"
        )

        async with aiohttp.ClientSession() as session:

            def raise_provisioning_exception(additional_note: str = ""):
                raise ProvisioningError(
                    "Error from provisioning API, invalid payload " + additional_note
                )

            api_url = f"{self.cloud.client.api_base_url}/{IOT_PROVISIONING_API_PATH}"
            provisioning_payload = {
                "sn": self.cloud.client.device_sn,
                "token": provisioning_key,
            }
            headers = {"Content-Type": "application/json"}
            response = await session.post(
                api_url, json=provisioning_payload, headers=headers
            )
            if response.status != 200:
                _LOGGER.error("Error from provisioning API (%s):", response.status)
                _LOGGER.error({response.text})

            try:
                j = await response.json()

                _LOGGER.info(json.dumps(j, indent=4))

                # mock_file = open("./test/mock/provisionning.json", "r")
                # j = json.load(mock_file)
                # mock_file.close()

                if "registration" in j:
                    error = j["registration"]["error"]
                    thing = j["registration"]["thing"]

                    if error is not None:
                        _LOGGER.error("Error from provisioning API :")
                        _LOGGER.error(error)
                        raise_provisioning_exception(
                            "Error from provisioning API :" + error
                        )
                    else:
                        config = await self.cloud.run_executor(
                            CloudConfig.persist_from_api_thing, thing, self.cloud.path()
                        )
                        _LOGGER.info(
                            "Successfully provisioned, with thing name: %s",
                            config.iot_thing_name,
                        )

                else:
                    _LOGGER.error("Error from provisioning API, invalid payload :")
                    _LOGGER.error(json.dumps(j))
                    raise_provisioning_exception(json.dumps(j))

            except json.JSONDecodeError:
                _LOGGER.error("Unknown Error")
