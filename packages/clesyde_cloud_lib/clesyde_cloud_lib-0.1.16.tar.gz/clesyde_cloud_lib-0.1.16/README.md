# Clesyde Cloud Lib

[![PyPI](https://img.shields.io/pypi/v/clesyde_cloud_lib.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/clesyde_cloud_lib.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/clesyde_cloud_lib)][python version]
[![License](https://img.shields.io/pypi/l/clesyde_cloud_lib)][license]

[![Read the documentation at https://clesyde_cloud_lib.readthedocs.io/](https://img.shields.io/readthedocs/clesyde_cloud_lib/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/fdewasmes/clesyde_cloud_lib/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/fdewasmes/clesyde_cloud_lib/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/clesyde_cloud_lib/
[status]: https://pypi.org/project/clesyde_cloud_lib/
[python version]: https://pypi.org/project/clesyde_cloud_lib
[read the docs]: https://clesyde_cloud_lib.readthedocs.io/
[tests]: https://github.com/fdewasmes/clesyde_cloud_lib/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/fdewasmes/clesyde_cloud_lib
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview

Clesyde Cloud Lib is a Python library that powers device connectivity with the Clesyde cloud backend. It provides:

- Provisioning: one-time registration of a device against a provisioning API to retrieve credentials (certificates/keys) and endpoints, then persists them locally.
- IoT messaging: an asynchronous MQTT client for AWS IoT Core using aiomqtt, handling connection lifecycle, subscriptions, and message routing.
- Remote access: secure remote UI connectivity via SniTun tunnels, with token refresh, certificate rotation handling, and connection life‑cycle management.
- A minimal CLI entry point (exposed as `clesyde_cloud_lib`) primarily for version reporting today.

If you are integrating a device or service with the Clesyde platform, this library provides the building blocks to provision, connect to IoT Core, react to platform commands, and manage secure remote access.

## Tech stack

- Language: Python
- Runtime: Python 3.12 (see `pyproject.toml`)
- Packaging/Build: Poetry
- CLI: Click
- Async HTTP: aiohttp
- MQTT: aiomqtt (MQTT v5)
- Remote tunnel: snitun
- Docs: Sphinx (with myst-parser, sphinx-click)
- Testing: pytest, coverage; optional nox sessions for automation

## Requirements

- Python 3.12+
- Supported platforms: Any OS supported by Python and the dependencies above.
- Network access to the configured endpoints for:
  - AWS IoT Core MQTT over TLS (default port 8883)
  - Remote snitun endpoint (default TCP 443)
- OpenSSL system trust store suitable for TLS operations

## Installation

From PyPI with pip:

```bash
pip install clesyde_cloud_lib
```

With Poetry (for development):

```bash
poetry install
```

## Usage

The library is intended to be embedded in a host application that implements the `ClesydeCloudClient` interface (see `src/clesydecloud/client.py`). Typical flow:

1) Create your client class implementing:
   - `device_sn` (device serial number)
   - `base_path` (where config/certs are stored; the library will use `<base_path>/.clesydecloud`)
   - `loop` (asyncio event loop)
   - `api_base_url` (provisioning API base)
   - `aiohttp_runner` (optional web runner hook)
2) Instantiate `ClesydeCloud(client)`.
3) Call `await cloud.initialize()` to load config and start IoT/Remote subsystems.
4) On shutdown, call `await cloud.stop()`.

Minimal CLI:

```bash
# Shows exit code 0 and supports --version
clesyde_cloud_lib --version
```

More advanced CLI commands are not implemented yet. TODO: Extend the CLI for provisioning and diagnostics.

See source modules for reference implementations:
- Provisioning: `src/clesydecloud/provisioning.py`
- IoT Core handling: `src/clesydecloud/iot.py`, `src/clesydecloud/iot_message.py`, `src/clesydecloud/iot_shadow.py`
- Remote access: `src/clesydecloud/remote.py`
- Data model and persistence: `src/clesydecloud/data.py`

## Configuration and environment variables

Configuration is persisted to files under `<base_path>/.clesydecloud/` during provisioning:

- `cloud_config.json` (IoT endpoint, thing name, remote endpoint, access point)
- `iot_ca.pem`, `iot_cert.pem`, `iot_key.pem` (AWS IoT Core trust and device credentials)
- `remote_cert.pem`, `remote_key.pem` (SniTun client cert/key)

Environment variables: none are required or used by the library at present. TODO: Document any future env vars (e.g., to override paths or endpoints).

## Entry points and scripts

- Console script: `clesyde_cloud_lib` → `clesydecloud.__main__:main` (Click). Currently reports version and exits.
- Import usage: `from clesydecloud import ClesydeCloud` and build around it using your own `ClesydeCloudClient` implementation.

## Running the tests

Using pytest directly:

```bash
pip install -e .[dev]  # or use Poetry
pytest -q
```

With Poetry:

```bash
poetry run pytest -q
```

With Nox (optional):

```bash
pip install nox nox-poetry
nox -s tests
nox -s coverage
```

Coverage configuration is in `pyproject.toml` (`fail_under = 100` by default).

## Project structure

```
.
├── src/clesydecloud/
│   ├── __init__.py            # ClesydeCloud core orchestrator
│   ├── __main__.py            # Minimal Click-based CLI entry point
│   ├── client.py              # Abstract client interface to embed in host app
│   ├── const.py               # Constants (paths, topics)
│   ├── data.py                # Config persistence and cert management
│   ├── iot.py                 # MQTT connection management (aiomqtt)
│   ├── iot_message.py         # Topic routing and message handlers
│   ├── iot_shadow.py          # Shadow model (dataclasses-json)
│   ├── remote.py              # Remote access via snitun
│   ├── provisioning.py        # Provisioning against API and persistence
│   ├── status.py              # Status dataclasses
│   └── utils.py               # Helpers (TLS context, regex, callbacks)
├── tests/                     # Pytest tests and helper scripts
├── docs/                      # Sphinx docs
├── pyproject.toml             # Poetry project config
├── noxfile.py                 # Nox sessions (lint, tests, docs, etc.)
└── LICENSE                    # GPL-3.0
```

## Development

- Install tooling with Poetry: `poetry install`
- Format/lint: `poetry run pre-commit run --all-files`
- Type check: `poetry run mypy src tests`
- Docs live build: `poetry run sphinx-build docs docs/_build`
- Nox sessions: `nox -l` to list available sessions

## Release and publishing

Releases are built from `pyproject.toml` using Poetry. Built artifacts are present under `dist/`. TODO: Document the exact release process (versioning, tagging, CI publish).

## License

Distributed under the terms of the GPL-3.0 license. See [LICENSE].

## Contributing

Contributions are very welcome. See the [Contributor Guide].

## Links

- Docs: [Read the Docs][read the docs] (may be a placeholder if not yet published)
- Issues: [GitHub Issues][file an issue]
- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

<!-- references -->

[LICENSE]: LICENSE
[Contributor Guide]: CONTRIBUTING.md
[file an issue]: https://github.com/fdewasmes/clesyde_cloud_lib/issues
