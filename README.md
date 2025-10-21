[![ Logo OpenStudioLandscapes ](https://github.com/michimussato/OpenStudioLandscapes/raw/main/media/images/logo128.png)](https://github.com/michimussato/OpenStudioLandscapes)

***

1. [Feature: OpenStudioLandscapes-Ayon](#feature-openstudiolandscapes-ayon)
   1. [Brief](#brief)
   2. [Requirements](#requirements)
   3. [Install](#install)
      1. [This Feature](#this-feature)
   4. [Add to OpenStudioLandscapes](#add-to-openstudiolandscapes)
   5. [Testing](#testing)
      1. [pre-commit](#pre-commit)
      2. [nox](#nox)
   6. [Variables](#variables)
      1. [Feature Configs](#feature-configs)
2. [Community](#community)
3. [Official Resources](#official-resources)
   1. [Official Documentation](#official-documentation)
      1. [Dev Resources](#dev-resources)

***

This `README.md` was dynamically created with [OpenStudioLandscapesUtil-ReadmeGenerator](https://github.com/michimussato/OpenStudioLandscapesUtil-ReadmeGenerator).

***

# Feature: OpenStudioLandscapes-Ayon

## Brief

This is an extension to the OpenStudioLandscapes ecosystem. The full documentation of OpenStudioLandscapes is available [here](https://github.com/michimussato/OpenStudioLandscapes).

You feel like writing your own Feature? Go and check out the [OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template).

## Requirements

- `python-3.11`
- `OpenStudioLandscapes`

## Install

### This Feature

Clone this repository into `OpenStudioLandscapes/.features`:

```shell
# cd .features
git clone https://github.com/michimussato/OpenStudioLandscapes-Ayon.git
```

Create `venv`:

```shell
# cd .features/OpenStudioLandscapes-Ayon
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
```

Configure `venv`:

```shell
# cd .features/OpenStudioLandscapes-Ayon
pip install -e "../../[dev]"
pip install -e ".[dev]"
```

For more info see [VCS Support of pip](https://pip.pypa.io/en/stable/topics/vcs-support/).

## Add to OpenStudioLandscapes

Add the following code to `OpenStudioLandscapes.engine.features.FEATURES`:

```python
FEATURES.update(
    "OpenStudioLandscapes-Ayon": {
        "enabled": True|False,
        # - from ENVIRONMENT VARIABLE (.env):
        #   "enabled": get_bool_env("ENV_VAR")
        # - combined:
        #   "enabled": True|False or get_bool_env(
        #       "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_AYON"
        #   )
        "module": "OpenStudioLandscapes.Ayon.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    }
)
```

## Testing

### pre-commit

- https://pre-commit.com
- https://pre-commit.com/hooks.html

```shell
pre-commit install
```

### nox

#### Generate Report

```shell
nox --no-error-on-missing-interpreters --report .nox/nox-report.json
```

#### Re-Generate this README

```shell
nox -v --add-timestamp --session readme
```

#### Generate Sphinx Documentation

```shell
nox -v --add-timestamp --session docs
```

#### pylint

```shell
nox -v --add-timestamp --session lint
```

##### pylint: disable=redefined-outer-name

- [`W0621`](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html): Due to Dagsters way of piping arguments into assets.

#### SBOM

Acronym for Software Bill of Materials

```shell
nox -v --add-timestamp --session sbom
```

We create the following SBOMs:

- [`cyclonedx-bom`](https://pypi.org/project/cyclonedx-bom/)
- [`pipdeptree`](https://pypi.org/project/pipdeptree/) (Dot)
- [`pipdeptree`](https://pypi.org/project/pipdeptree/) (Mermaid)

SBOMs for the different Python interpreters defined in [`.noxfile.VERSIONS`](https://github.com/michimussato/OpenStudioLandscapes-Ayon/tree/main/noxfile.py) will be created in the [`.sbom`](https://github.com/michimussato/OpenStudioLandscapes-Ayon/tree/main/.sbom) directory of this repository.

- `cyclone-dx`
- `pipdeptree` (Dot)
- `pipdeptree` (Mermaid)

Currently, the following Python interpreters are enabled for testing:

- `python3.11`

## Variables

The following variables are being declared in `OpenStudioLandscapes.Ayon.constants` and are accessible throughout the [`OpenStudioLandscapes-Ayon`](https://github.com/michimussato/OpenStudioLandscapes-Ayon/tree/main/src/OpenStudioLandscapes/Ayon/constants.py) package.

| Variable                  | Type   |
| :------------------------ | :----- |
| `DOCKER_USE_CACHE`        | `bool` |
| `AYONDB_INSIDE_CONTAINER` | `bool` |
| `ASSET_HEADER`            | `dict` |
| `FEATURE_CONFIGS`         | `dict` |

### Feature Configs

#### Feature Config: default

| Variable                      | Type   | Value                                                      |
| :---------------------------- | :----- | :--------------------------------------------------------- |
| `DOCKER_USE_CACHE`            | `bool` | `False`                                                    |
| `HOSTNAME`                    | `str`  | `ayon`                                                     |
| `TELEPORT_ENTRY_POINT_HOST`   | `str`  | `{{HOSTNAME}}`                                             |
| `TELEPORT_ENTRY_POINT_PORT`   | `str`  | `{{AYON_PORT_HOST}}`                                       |
| `CONFIGS_ROOT`                | `str`  | `{DOT_FEATURES}/OpenStudioLandscapes-Ayon/.payload/config` |
| `AYON_PORT_HOST`              | `str`  | `5005`                                                     |
| `AYON_PORT_CONTAINER`         | `str`  | `5000`                                                     |
| `AYON_DB_INSTALL_DESTINATION` | `str`  | `{DOT_LANDSCAPES}/{LANDSCAPE}/Ayon__Ayon/data/ayon-db`     |

# Community

| Feature                             | GitHub                                                                                                                                     | Discord                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| OpenStudioLandscapes                | [https://github.com/michimussato/OpenStudioLandscapes](https://github.com/michimussato/OpenStudioLandscapes)                               | [# openstudiolandscapes-general](https://discord.gg/F6bDRWsHac)        |
| OpenStudioLandscapes-Ayon           | [https://github.com/michimussato/OpenStudioLandscapes-Ayon](https://github.com/michimussato/OpenStudioLandscapes-Ayon)                     | [# openstudiolandscapes-ayon](https://discord.gg/gd6etWAF3v)           |
| OpenStudioLandscapes-Dagster        | [https://github.com/michimussato/OpenStudioLandscapes-Dagster](https://github.com/michimussato/OpenStudioLandscapes-Dagster)               | [# openstudiolandscapes-dagster](https://discord.gg/jwB3DwmKvs)        |
| OpenStudioLandscapes-Kitsu          | [https://github.com/michimussato/OpenStudioLandscapes-Kitsu](https://github.com/michimussato/OpenStudioLandscapes-Kitsu)                   | [# openstudiolandscapes-kitsu](https://discord.gg/6cc6mkReJ7)          |
| OpenStudioLandscapes-RustDeskServer | [https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer](https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer) | [# openstudiolandscapes-rustdeskserver](https://discord.gg/nJ8Ffd2xY3) |
| OpenStudioLandscapes-Template       | [https://github.com/michimussato/OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template)             | [# openstudiolandscapes-template](https://discord.gg/J59GYp3Wpy)       |
| OpenStudioLandscapes-Twingate       | [https://github.com/michimussato/OpenStudioLandscapes-Twingate](https://github.com/michimussato/OpenStudioLandscapes-Twingate)             | [# openstudiolandscapes-twingate](https://discord.gg/tREYa6UNJf)       |

To follow up on the previous LinkedIn publications, visit:

- [OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/company/106731439/).
- [Search for tag #OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/search/results/all/?keywords=%23openstudiolandscapes).

***

# Official Resources

[![Logo Ayon ](https://ynput.io/wp-content/uploads/2023/04/ayon-whiteg-dot.svg)](https://ynput.io/ayon/)

Ayon is written and maintained by Ynput, a company based in Czech Republic:

[![Logo Ynput ](https://ynput.io/wp-content/uploads/2022/09/ynput-logo-small-bg.svg)](https://ynput.io)

Ynput offers different versions of Ayon

- Community
- Pro Cloud
- Studio Cloud

`OpenStudioLandscapes-Ayon` is based on the [Community](https://ynput.io/ayon/pricing/) version provided by their own Docker image:

- [https://github.com/ynput/ayon-docker](https://github.com/ynput/ayon-docker)

## Official Documentation

- [Features](https://docs.ayon.dev/features)
- [User Docs](https://docs.ayon.dev/docs/artist_getting_started)
- [Admin Docs](https://docs.ayon.dev/docs/system_introduction)
- [Dev Docs](https://docs.ayon.dev/docs/dev_introduction)

### Dev Resources

- [REST API Docs](https://docs.ayon.dev/api)
- [GraphQL API Explorer](https://playground.ayon.app/explorer)
- [Python API Docs](https://docs.ayon.dev/ayon-python-api)
- [C++ API Docs](https://docs.ayon.dev/ayon-cpp-api)
- [USD Resolver Docs](https://docs.ayon.dev/ayon-usd-resolver)
- [Frontend React Components](https://components.ayon.dev)

***