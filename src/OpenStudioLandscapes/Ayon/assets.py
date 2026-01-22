import copy
import enum
import pathlib
from collections import ChainMap
from functools import reduce
from typing import Dict, Generator, List, Union

import git
import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)
from docker_compose_graph.utils import *
from docker_compose_graph.yaml_tags.overrides import *
from git.exc import GitCommandError
from OpenStudioLandscapes.engine.common_assets.cmd import get_feature__cmd

# from OpenStudioLandscapes.engine.common_assets.compose_scope import (
#     get_compose_scope_group__cmd,
# )
from OpenStudioLandscapes.engine.common_assets.docker_compose_graph import (
    get_docker_compose_graph,
)
from OpenStudioLandscapes.engine.common_assets.feature import get_feature__CONFIG
from OpenStudioLandscapes.engine.common_assets.feature_out import get_feature_out_v2
from OpenStudioLandscapes.engine.common_assets.group_in import (
    get_feature_in,
    get_feature_in_parent,
)
from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out
from OpenStudioLandscapes.engine.config.models import ConfigEngine
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker.compose_dicts import *

from OpenStudioLandscapes.Ayon import dist
from OpenStudioLandscapes.Ayon.config.models import CONFIG_STR, Config
from OpenStudioLandscapes.Ayon.constants import *

# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    data_type=enum.Enum,
    representer=yaml.representer.SafeRepresenter.represent_str,
)


cmd: AssetsDefinition = get_feature__cmd(
    ASSET_HEADER=ASSET_HEADER,
)


CONFIG: AssetsDefinition = get_feature__CONFIG(
    ASSET_HEADER=ASSET_HEADER,
    CONFIG_STR=CONFIG_STR,
    search_model_of_type=Config,
)


feature_in: AssetsDefinition = get_feature_in(
    ASSET_HEADER=ASSET_HEADER,
    ASSET_HEADER_BASE=ASSET_HEADER_BASE,
    ASSET_HEADER_FEATURE_IN={},
)


group_out: AssetsDefinition = get_group_out(
    ASSET_HEADER=ASSET_HEADER,
)


docker_compose_graph: AssetsDefinition = get_docker_compose_graph(
    ASSET_HEADER=ASSET_HEADER,
)


feature_out_v2: AssetsDefinition = get_feature_out_v2(
    ASSET_HEADER=ASSET_HEADER,
)


# Produces
# - feature_in_parent
# - CONFIG_PARENT
# if ConfigParent is or type FeatureBaseModel
feature_in_parent: Union[AssetsDefinition, None] = get_feature_in_parent(
    ASSET_HEADER=ASSET_HEADER,
    config_parent=ConfigParent,
)


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
    },
)
def clone_repository(
    context: AssetExecutionContext,
    CONFIG: Config,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    env: dict = CONFIG.env

    repo_dir = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{dist.name}",
        "__".join(context.asset_key.path),
        "repos",
    )

    repository_dir_full = repo_dir / CONFIG.repository_subdir
    repository_dir_full.parent.mkdir(parents=True, exist_ok=True)

    try:
        git.Repo.clone_from(
            url=str(CONFIG.repository_url),
            to_path=repository_dir_full,
            branch=CONFIG.repository_branch,
        )
    except GitCommandError as e:
        context.log.warning("Pulling from Repo (%s)" % e)
        existing_repo = git.Repo(repository_dir_full)
        origin = existing_repo.remotes.origin
        origin.pull()

    yield Output(repository_dir_full)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(repository_dir_full),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
    },
)
def compose_networks(
    context: AssetExecutionContext,
    CONFIG: Config,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[Dict[str, Dict[str, Dict[str, str]]]] | AssetMaterialization,
    None,
    None,
]:

    env: Dict = CONFIG.env

    compose_network_mode = DockerComposePolicies.NETWORK_MODE.DEFAULT

    docker_dict = get_network_dicts(
        context=context,
        compose_network_mode=compose_network_mode,
        env=env,
    )

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "compose_network_mode": MetadataValue.text(compose_network_mode.value),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
        },
    )


# Todo:
#  - [ ] Maybe fix this Non-Standard `compose` implementation
@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
        "compose_networks": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
        ),
        "clone_repository": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "clone_repository"]),
        ),
    },
)
def compose(
    context: AssetExecutionContext,
    CONFIG: Config,  # pylint: disable=redefined-outer-name
    compose_networks: Dict,  # pylint: disable=redefined-outer-name
    clone_repository: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[Dict[str, List[Dict[str, List[str]]]]] | AssetMaterialization,
    None,
    None,
]:
    """
    Non-standard (non-factory) implementation of `compose` Asset
    Other non-standard examples:
        - `OpenStudioLandscapes.Ayon.assets.compose`
        - `OpenStudioLandscapes.VERT.assets.compose`
        - `OpenStudioLandscapes.OpenCue.assets.compose`

    Args:
        context:
        compose_networks:
        clone_repository:
        CONFIG:

    Returns:

    """

    env: Dict = CONFIG.env

    config_engine: ConfigEngine = CONFIG.config_engine

    docker_compose_override: pathlib.Path = CONFIG.docker_compose_override_expanded
    context.log.debug(f"{docker_compose_override = }")
    docker_compose_override.parent.mkdir(parents=True, exist_ok=True)

    network_dict = {}
    ports_dict = {}

    if "networks" in compose_networks:
        network_dict = {"networks": list(compose_networks.get("networks", {}).keys())}
        ports_dict = {
            "ports": OverrideArray(
                [
                    f"{CONFIG.ayon_port_host}:{CONFIG.ayon_port_container}",
                ]
            ),
        }
    elif "network_mode" in compose_networks:
        network_dict = {"network_mode": compose_networks.get("network_mode")}

    parent = clone_repository / CONFIG.docker_compose_yml

    ayon_db_dir_host = (
        pathlib.Path(CONFIG.ayon_db_install_destination_expanded) / "postgresql"
    )
    ayon_db_dir_host.mkdir(parents=True, exist_ok=True)
    context.log.info(f"Directory {ayon_db_dir_host.as_posix()} created.")

    volumes_dict = {
        "volumes": [
            f"{ayon_db_dir_host.as_posix()}:/var/lib/postgresql/data:rw",
        ]
    }

    # For portability, convert absolute volume paths to relative paths

    _volume_relative = []

    for v in volumes_dict["volumes"]:

        host, container = v.split(":", maxsplit=1)

        volume_dir_host_rel_path = get_relative_path_via_common_root(
            context=context,
            # path_src=pathlib.Path(env["DOCKER_COMPOSE"]),
            # This leads to a wrong relative path (missing one "parent")
            # path element.
            # It uses {DOT_LANDSCAPES}/{LANDSCAPE}/Ayon__Ayon/Ayon__DOCKER_COMPOSE/docker_compose/docker-compose.yml
            # as the starting point but does not lead to the correct resolution.
            # In fact, it seems like the actual CWD for this is the docker-compose.yml
            # from the repo (main entry point) which seems to lead to an incorrect amount
            # of `cd ..` actions.
            # Let's try with the yml from the repo as the path_src instead of the one from
            # "DOCKER_COMPOSE"
            # => seems to do the trick to make sure, we end up using the directory
            # we intended to use
            path_src=CONFIG.docker_compose_expanded,
            path_dst=pathlib.Path(host),
            path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
        )

        _volume_relative.append(
            f"{volume_dir_host_rel_path.as_posix()}:{container}",
        )

    volumes_dict = {
        "volumes": [
            "/etc/localtime:/etc/localtime:ro",
            *_volume_relative,
        ]
    }

    service_name_postgres = "postgres"
    container_name_postgres, host_name_postgres = get_docker_compose_names(
        context=context,
        service_name=service_name_postgres,
        landscape_id=env.get("LANDSCAPE", "default"),
        domain_lan=config_engine.openstudiolandscapes__domain_lan,
    )

    service_name_redis = "redis"
    container_name_redis, host_name_redis = get_docker_compose_names(
        context=context,
        service_name=service_name_redis,
        landscape_id=env.get("LANDSCAPE", "default"),
        domain_lan=config_engine.openstudiolandscapes__domain_lan,
    )

    service_name_server = "server"
    container_name_server, host_name_server = get_docker_compose_names(
        context=context,
        service_name=service_name_server,
        landscape_id=env.get("LANDSCAPE", "default"),
        domain_lan=config_engine.openstudiolandscapes__domain_lan,
    )

    docker_dict_override = {
        "services": {
            service_name_postgres: {
                "container_name": container_name_postgres,
                "hostname": host_name_postgres,
                "domainname": config_engine.openstudiolandscapes__domain_lan,
                **copy.deepcopy(volumes_dict),
                **copy.deepcopy(network_dict),
            },
            service_name_redis: {
                "container_name": container_name_redis,
                "hostname": host_name_redis,
                "domainname": config_engine.openstudiolandscapes__domain_lan,
                **copy.deepcopy(network_dict),
            },
            service_name_server: {
                "container_name": container_name_server,
                "hostname": host_name_server,
                "domainname": config_engine.openstudiolandscapes__domain_lan,
                # Todo:
                #  - [ ] healthcheck failure: https://github.com/ynput/ayon-docker/issues/34
                #  - [ ] Need to find out whether `ports` Override
                #  also overrides the exports in the source ayon-docker-compose.yml
                #  "exports": OverrideArray([]),
                **copy.deepcopy(network_dict),
                **copy.deepcopy(ports_dict),
            },
        },
    }

    if "networks" in compose_networks:
        network_dict = copy.deepcopy(compose_networks)
    else:
        network_dict = {}

    docker_chainmap = ChainMap(
        network_dict,
        docker_dict_override,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)

    docker_yaml_override: str = yaml.dump(docker_dict)

    with open(docker_compose_override, "w") as fw:
        fw.write(docker_yaml_override)

    # Write compose override to disk here to be able to reference
    # it in the following step.
    # It seems that it's necessary to apply overrides in
    # include: path

    # Convert absolute paths in `include` to
    # relative ones
    DOCKER_COMPOSE = CONFIG.docker_compose_expanded
    DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

    rel_paths = []
    dot_landscapes = pathlib.Path(env["DOT_LANDSCAPES"])

    for path in [
        parent,
        CONFIG.docker_compose_override_expanded,
    ]:
        rel_path = get_relative_path_via_common_root(
            context=context,
            path_src=CONFIG.docker_compose_expanded,
            path_dst=path,
            path_common_root=dot_landscapes,
        )

        rel_paths.append(rel_path.as_posix())

    docker_dict_include = {
        "include": [
            {
                "path": rel_paths,
            },
        ],
    }

    docker_yaml_include = yaml.dump(docker_dict_include)

    # Write docker-compose.yaml
    with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
        fw.write(docker_yaml_include)

    yield Output(docker_dict_include)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict_include),
            "docker_yaml_override": MetadataValue.md(
                f"```yaml\n{docker_yaml_override}\n```"
            ),
            "path_docker_yaml_override": MetadataValue.path(DOCKER_COMPOSE),
        },
    )
