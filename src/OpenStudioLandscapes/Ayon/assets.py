# pylint: disable=line-too-long,invalid-name
import copy
import enum
import json
import pathlib
import textwrap
from collections import ChainMap
from functools import reduce
from typing import Any, Dict, Generator, List, Union

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
from docker_compose_graph.utils import (
    deep_merge,
)
from docker_compose_graph.yaml_tags.overrides import (
    OverrideArray,
)
from git.exc import GitCommandError
from OpenStudioLandscapes.engine.common_assets import (  # compose,
    cmd,
    docker_compose_graph,
    feature,
    feature_out,
    group_in,
    group_out,
)
from OpenStudioLandscapes.engine.env.configurable_resources.config_engine import ConfigEngineConfigurableResource
from OpenStudioLandscapes.engine.constants import (
    ASSET_HEADER_BASE,
    ConfigParent,
)
from OpenStudioLandscapes.engine.enums import (
    DockerComposePolicies,
)
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesFeatureIn
from OpenStudioLandscapes.engine.utils import (
    get_docker_compose_names,
    get_relative_path_via_common_root,
)
from OpenStudioLandscapes.engine.utils.docker.compose_dicts import get_network_dicts

from OpenStudioLandscapes.Ayon import (
    ASSET_HEADER,
    config,
    dist,
)

# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    data_type=enum.Enum,
    representer=yaml.representer.SafeRepresenter.represent_str,
)


cmd: AssetsDefinition = cmd.get_feature__cmd(
    ASSET_HEADER=ASSET_HEADER,
)


CONFIG: AssetsDefinition = feature.get_feature__CONFIG(
    ASSET_HEADER=ASSET_HEADER,
    CONFIG_STR=config.models.CONFIG_STR,
    search_model_of_type=config.models.Config,
)


feature_in: AssetsDefinition = group_in.get_feature_in(
    ASSET_HEADER=ASSET_HEADER,
    ASSET_HEADER_BASE=ASSET_HEADER_BASE,
    ASSET_HEADER_FEATURE_IN={},
)


group_out: AssetsDefinition = group_out.get_group_out(
    ASSET_HEADER=ASSET_HEADER,
)


docker_compose_graph: AssetsDefinition = docker_compose_graph.get_docker_compose_graph(
    ASSET_HEADER=ASSET_HEADER,
)


feature_out_v2: AssetsDefinition = feature_out.get_feature_out_v2(
    ASSET_HEADER=ASSET_HEADER,
)


# Produces
# - feature_in_parent
# - CONFIG_PARENT
# if ConfigParent is or type FeatureBaseModel
feature_in_parent: Union[AssetsDefinition, None] = group_in.get_feature_in_parent(
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
    CONFIG: config.models.Config,  # pylint: disable=redefined-outer-name
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
            url=CONFIG.repository_url,
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
    CONFIG: config.models.Config,  # pylint: disable=redefined-outer-name
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


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
        "feature_in": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "feature_in"]),
        ),
    },
    description=textwrap.dedent("""
        Help on server deployment with `settings.json`:
        - [AYON Server Local Deployment](https://help.ayon.app/en/help/articles/2293963-ayon-server-local-deployment)
        - [AYON Server Provisioning](https://help.ayon.app/en/articles/4089565-ayon-server-provisioning)
        - [template.json](https://github.com/ynput/ayon-docker/blob/main/settings/template.json)
        """),
)
def setup_json(
    context: AssetExecutionContext,
    CONFIG: config.models.Config,  # pylint: disable=redefined-outer-name
    feature_in: OpenStudioLandscapesFeatureIn,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization | Any, None, None]:

    env: Dict = CONFIG.env

    setup_template_json_path = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{dist.name}",
        "settings",
        "setup_template.json",
    ).expanduser()

    setup_template_json_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    compose_project_name = (
        f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{CONFIG.compose_scope}"
    )

    context.log.debug(CONFIG.config_engine)

    docker_config_json: pathlib.Path = (
        feature_in.openstudiolandscapes_base.docker_config_json
    )

    # Run this command to deploy a vanilla Ayon server
    # - creates default values like users for example
    # - if the user already exists, it won't edit it
    # - Todo:
    #    - [ ] security concern: run this script
    #          and create admins. Fine for now.
    setup_command = [
        "$(which docker)",
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--project-name",
        compose_project_name,
        "exec",
        "--no-tty",
        "server",
        f"python -m setup - < {setup_template_json_path.as_posix()}",
    ]

    setup_template_json_dict: Dict = copy.deepcopy(CONFIG.setup_template)

    context.log.debug(f"{setup_template_json_dict = }")

    with open(setup_template_json_path, "w") as fw:
        json.dump(setup_template_json_dict, fw, indent=2)

    yield Output(setup_template_json_path)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(
                setup_template_json_path
            ),
            "setup_json": MetadataValue.md(
                f"```json\n{setup_template_json_path.read_text(encoding='utf-8')}\n```"
            ),
            "setup_command": MetadataValue.path(" ".join(setup_command)),
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
        # "setup_json": AssetIn(
        #     AssetKey([*ASSET_HEADER["key_prefix"], "setup_json"]),
        # ),
    },
)
def compose(
    context: AssetExecutionContext,
    config_ConfigEngineConfigurableResource: ConfigEngineConfigurableResource,
    CONFIG: config.models.Config,  # pylint: disable=redefined-outer-name
    compose_networks: Dict,  # pylint: disable=redefined-outer-name
    clone_repository: pathlib.Path,  # pylint: disable=redefined-outer-name
    # setup_json: pathlib.Path,  # pylint: disable=redefined-outer-name
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

    config_engine: ConfigEngineConfigurableResource = config_ConfigEngineConfigurableResource

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

    # postgres service
    # We just need to add postgresql as a subdirectory so that
    # Postgres can set its own permissions
    ayon_db_dir_host = (
        pathlib.Path(CONFIG.ayon_db_install_destination_expanded) / "postgresql"
    )
    ayon_db_dir_host.mkdir(parents=True, exist_ok=True)
    context.log.info(f"Directory {ayon_db_dir_host.as_posix()} created.")

    volumes_dict_postgres = {
        "volumes": [
            f"{ayon_db_dir_host.as_posix()}:/var/lib/postgresql/data:rw",
        ]
    }

    # For portability, convert absolute volume paths to relative paths

    _volume_relative = []

    for v in volumes_dict_postgres["volumes"]:

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

    volumes_dict_postgres = {
        "volumes": list(
            {
                "/etc/localtime:/etc/localtime:ro",
                *_volume_relative,
                *config_engine.global_bind_volumes,
                *CONFIG.local_bind_volumes,
            }
        )
    }

    # server service
    CONFIG.ayon_addons_dir_expanded.mkdir(parents=True, exist_ok=True)
    context.log.info(f"Directory {CONFIG.ayon_addons_dir_expanded.as_posix()} created.")
    CONFIG.ayon_storage_dir_expanded.mkdir(parents=True, exist_ok=True)
    context.log.info(
        f"Directory {CONFIG.ayon_storage_dir_expanded.as_posix()} created."
    )
    # CONFIG.ayon_backend_dir_expanded.mkdir(parents=True, exist_ok=True)
    # context.log.info(f"Directory {CONFIG.ayon_backend_dir_expanded.as_posix()} created.")

    volumes_dict_server = {
        "volumes": [
            f"{CONFIG.ayon_addons_dir_expanded.as_posix()}:/addons:rw",
            f"{CONFIG.ayon_storage_dir_expanded.as_posix()}:/storage:rw",
            # f"{setup_json.as_posix()}:/settings/setup.json:ro",
            # f"{CONFIG.ayon_backend_dir_expanded.as_posix()}:/backend:rw",
        ]
    }

    # For portability, convert absolute volume paths to relative paths

    _volume_relative = []

    for v in volumes_dict_server["volumes"]:

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

    volumes_dict_server = {
        "volumes": list(
            {
                "/etc/localtime:/etc/localtime:ro",
                *_volume_relative,
                *config_engine.global_bind_volumes,
                *CONFIG.local_bind_volumes,
            }
        )
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
                **copy.deepcopy(volumes_dict_postgres),
                **copy.deepcopy(network_dict),
                "environment": {
                    "TZ": config_engine.tz,
                    **config_engine.global_environment_variables,
                },
            },
            service_name_redis: {
                "container_name": container_name_redis,
                "hostname": host_name_redis,
                "domainname": config_engine.openstudiolandscapes__domain_lan,
                **copy.deepcopy(network_dict),
                "environment": {
                    "TZ": config_engine.tz,
                    **config_engine.global_environment_variables,
                },
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
                # Setup:
                # SERVER_CONTAINER=server
                # SETUP_CMD=docker compose exec -T $(SERVER_CONTAINER) python -m setup
                # AYON_STACK_SETTINGS_FILE ?= settings/template.json
                # $(SETUP_CMD) - < $(AYON_STACK_SETTINGS_FILE)
                "environment": {
                    "TZ": config_engine.tz,
                    **config_engine.global_environment_variables,
                    **CONFIG.local_environment_variables,
                },
                **copy.deepcopy(network_dict),
                **copy.deepcopy(ports_dict),
                **copy.deepcopy(volumes_dict_server),
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
                # Todo
                #  - [x] https://help.ayon.app/en/articles/4089565-ayon-server-provisioning
                #        https://github.com/michimussato/OpenStudioLandscapesSetup-Faranna/commit/c90a8bd9de1bc5fd55f0f6c254ae734d150991a4
                #        Do we have to set
                #        the project_directory:?
                #        Looks like the database ends up
                #        in the wrong directory
                #        ayon_db_install_destination: '{DOT_LANDSCAPES}/.persistent/{FEATURE}/data/ayon-db'
                #        Results in:
                #        ../../../.persistent/OpenStudioLandscapes-Ayon/data/ayon-db/postgresql:/var/lib/postgresql/data:rw
                #        /data/.openstudiolandscapes/.landscapes/2026-02-09_11-54-04__sideways-principled-festive-newt/OpenStudioLandscapes-Ayon/.persistent/OpenStudioLandscapes-Ayon/data/ayon-db
                #        Is it relative to
                #        {
                #          "include": [
                #            {
                #              "path": [
                #   -->          "../../../2026-02-09_11-54-04__sideways-principled-festive-newt/OpenStudioLandscapes-Ayon/OpenStudioLandscapes_Ayon__clone_repository/repos/ayon-docker/docker-compose.yml",
                #                "../../../2026-02-09_11-54-04__sideways-principled-festive-newt/OpenStudioLandscapes-Ayon/docker_compose/docker-compose.override.yml"
                #              ]
                #            }
                #          ]
                #        }
                #
                #        ls -al /data/.openstudiolandscapes/.landscapes/2026-02-09_11-54-04__sideways-principled-festive-newt/OpenStudioLandscapes-Ayon/.persistent
                #        lrwxrwxrwx 1 root root 51 Jun  4 16:32 /data/.openstudiolandscapes/.landscapes/2026-02-09_11-54-04__sideways-principled-festive-newt/OpenStudioLandscapes-Ayon/.persistent -> /data/.openstudiolandscapes/.landscapes/.persistent
                #
                #        cat /data/.openstudiolandscapes/.landscapes/2026-02-09_11-54-04__sideways-principled-festive-newt/OpenStudioLandscapes-Ayon/OpenStudioLandscapes_Ayon__clone_repository/repos/ayon-docker/settings/template.json
                #        {
                #            "users": [
                #                {
                #                    "name": "admin",
                #                    "password": "admin",
                #                    "fullName": "Ayon admin",
                #                    "isAdmin": true
                #                },
                #                {
                #                    "name": "service",
                #                    "apiKey": "veryinsecurapikey",
                #                    "isService": true
                #                }
                #            ]
                #        }
                "project_directory": ".",  # This makes sure that all relative paths refer to the directory where THIS docker-compose file lives
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
