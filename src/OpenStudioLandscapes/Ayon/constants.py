__all__ = [
    "DOCKER_USE_CACHE",
    "AYONDB_INSIDE_CONTAINER",
    "ASSET_HEADER",
    "FEATURE_CONFIGS",
]

import pathlib
from pathlib import Path
from typing import Any, Generator

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    AssetOut,
    MetadataValue,
    Output,
    get_dagster_logger,
    multi_asset,
)

LOGGER = get_dagster_logger(__name__)

from OpenStudioLandscapes.engine.constants import DOCKER_USE_CACHE_GLOBAL
from OpenStudioLandscapes.engine.enums import OpenStudioLandscapesConfig, FeatureVolumeType

DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False
# Todo:
#  - [ ] AYONDB_INSIDE_CONTAINER = True raises NotImplementedError
AYONDB_INSIDE_CONTAINER = False


GROUP = "Ayon"
KEY = [GROUP]
FEATURE = f"OpenStudioLandscapes-{GROUP}".replace("_", "-")

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
}


# @formatter:off
FEATURE_CONFIGS = {
    OpenStudioLandscapesConfig.DEFAULT: {
        "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
        "HOSTNAME": "ayon",
        "TELEPORT_ENTRY_POINT_HOST": "{{HOSTNAME}}",  # Either a hardcoded str or a ref to a Variable (with double {{ }}!)
        "TELEPORT_ENTRY_POINT_PORT": "{{AYON_PORT_HOST}}",  # Either a hardcoded str or a ref to a Variable (with double {{ }}!)
        "CONFIGS_ROOT": pathlib.Path(
            "{DOT_FEATURES}",
            FEATURE,
            ".payload",
            "config",
        )
        .expanduser()
        .as_posix(),
        "AYON_PORT_HOST": "5005",
        "AYON_PORT_CONTAINER": "5000",
        # Todo
        #  - [ ] Could be implemented at some point
        #        for now: no user/pass gets created for new DB:
        #        https://docs.ayon.dev/docs/admin_server_deployment#installation
        # "AYON_USERNAME": None,
        # "AYON_PASSWORD": None,
        "AYON_DB_INSTALL_DESTINATION": {
            FeatureVolumeType.CONTAINED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                "{LANDSCAPE}",
                f"{GROUP}__{'__'.join(KEY)}",
                "data",
                "ayon-db",
            )
            .expanduser()
            .as_posix(),
            FeatureVolumeType.SHARED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                "{DOT_SHARED_VOLUMES}",
                f"{GROUP}__{'__'.join(KEY)}",
                "data",
                "ayon-db",
            )
            .expanduser()
            .as_posix(),
        }[FeatureVolumeType.CONTAINED]
    },
    # OpenStudioLandscapesConfig.DEVELOPMENT: {
    #     "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
    #     "CONFIGS_ROOT": pathlib.Path(
    #         get_configs_root(pathlib.Path(__file__)),
    #     )
    #     .expanduser()
    #     .as_posix(),
    #     "AYON_PORT_HOST": "5015",
    #     "AYON_PORT_CONTAINER": "5000",
    # },
}
# @formatter:on


# Todo:
#  - [ ] move to common_assets
@multi_asset(
    name=f"constants_{GROUP}",
    outs={
        "NAME": AssetOut(
            **ASSET_HEADER,
            dagster_type=str,
            description="",
        ),
        "FEATURE_CONFIGS": AssetOut(
            **ASSET_HEADER,
            dagster_type=dict,
            description="",
        ),
        "DOCKER_COMPOSE": AssetOut(
            **ASSET_HEADER,
            dagster_type=pathlib.Path,
            description="",
        ),
    },
)
def constants_multi_asset(
    context: AssetExecutionContext,
) -> Generator[
    Output[dict[OpenStudioLandscapesConfig, dict[str, bool | str]]]
    | AssetMaterialization
    | Output[Any]
    | Output[Path]
    | Any,
    None,
    None,
]:
    """ """

    yield Output(
        output_name="FEATURE_CONFIGS",
        value=FEATURE_CONFIGS,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("FEATURE_CONFIGS"),
        metadata={
            "__".join(
                context.asset_key_for_output("FEATURE_CONFIGS").path
            ): MetadataValue.json(FEATURE_CONFIGS),
        },
    )

    yield Output(
        output_name="NAME",
        value=__name__,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("NAME"),
        metadata={
            "__".join(context.asset_key_for_output("NAME").path): MetadataValue.path(
                __name__
            ),
        },
    )

    docker_compose = pathlib.Path(
        "{DOT_LANDSCAPES}",
        "{LANDSCAPE}",
        f"{ASSET_HEADER['group_name']}__{'_'.join(ASSET_HEADER['key_prefix'])}",
        "__".join(context.asset_key_for_output("DOCKER_COMPOSE").path),
        "docker_compose",
        "docker-compose.yml",
        # Todo
        #  - [ ] actually use "docker-compose.override.yml" in this Feature?
    )

    yield Output(
        output_name="DOCKER_COMPOSE",
        value=docker_compose,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("DOCKER_COMPOSE"),
        metadata={
            "__".join(
                context.asset_key_for_output("DOCKER_COMPOSE").path
            ): MetadataValue.path(docker_compose),
        },
    )
