"""Constants."""

from __future__ import annotations

CONFIG_DIR = ".clesydecloud"

IOT_PROVISIONING_API_PATH = "device/register"

CONFIG_FILE = "cloud_config.json"

IOT_CA_FILE = "iot_ca.pem"
IOT_CERT_FILE = "iot_cert.pem"
IOT_KEY_FILE = "iot_key.pem"
REMOTE_CERT_FILE = "remote_cert.pem"
REMOTE_KEY_FILE = "remote_key.pem"

IOT_PLATFORM_TOPIC = "c/platform"

IOT_THING_D2P_PREFIX = "c/d"
IOT_THING_SHADOW_TOPIC_PREFIX = "$aws/things"

IOT_THING_TOPIC_STATUS_SUFFIX = "status"
