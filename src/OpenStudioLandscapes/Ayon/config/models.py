import enum
import pathlib
from typing import List

from dagster import get_dagster_logger
from pydantic import (
    Field,
    HttpUrl,
    PositiveInt,
)

LOGGER = get_dagster_logger(__name__)

from OpenStudioLandscapes.engine.config.str_gen import get_config_str
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

from OpenStudioLandscapes.Ayon import dist, constants


class Branches(enum.StrEnum):
    main = "main"


class Config(FeatureBaseModel):

    feature_name: str = dist.name

    group_name: str = constants.ASSET_HEADER["group_name"]

    key_prefixes: List[str] = constants.ASSET_HEADER["key_prefix"]

    docker_compose_override: pathlib.Path = Field(
        default=pathlib.Path(
            "{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.override.yml"
        ),
        description="The path to the `docker-compose.yml` file.",
        frozen=True,
    )

    ayon_port_container: PositiveInt = Field(
        default=5000,
        description="The Ayon container port.",
        frozen=True,
    )
    ayon_port_host: PositiveInt = Field(
        default=5005,
        description="The Ayon host port.",
        frozen=False,
    )
    ayon_db_install_destination: pathlib.Path = Field(
        description="The host side Ayon database installation destination.",
        default=pathlib.Path("{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/data/ayon-db"),
    )
    # Todo:
    #  - [ ] Implement?
    # ayon_db_inside_container: bool = Field(
    #     default=False,
    #     description="The Ayon database inside container; the database will not be persistent. "
    #     "Helpful for testing.",
    # )

    # Todo:
    #  - [ ] is this necessary here?
    # @field_validator("ayon_port_container")
    # @classmethod
    # def ensure_valid__ayon_port_container(cls, value: int):
    #     if value == 80:
    #         return value
    #     else:
    #         raise ValueError(
    #             "`ayon_port_container` must be set "
    #             "to 80 for now. Other values *may* render Ayon inoperable."
    #         )

    repository_url: HttpUrl = Field(
        default="https://github.com/ynput/ayon-docker.git",
    )
    repository_branch: Branches = Field(
        default=Branches.main,
        description="The branch of the Ayon repository.",
        frozen=True,
        examples=[i.name for i in Branches],
    )
    repository_subdir: str = Field(
        default="ayon-docker",
    )
    docker_compose_yml: str = Field(
        default="docker-compose.yml",
    )
    docker_compose_worker_yml: str = Field(
        default="docker-compose.worker.yml",
    )

    # EXPANDABLE PATHS
    @property
    def docker_compose_override_expanded(self) -> pathlib.Path:
        LOGGER.debug(f"{self.env = }")
        if self.env is None:
            raise KeyError("`env` is `None`.")
        LOGGER.debug(f"Expanding {self.docker_compose_override}...")
        ret = pathlib.Path(
            self.docker_compose_override.expanduser()
            .as_posix()
            .format(
                **{
                    "FEATURE": self.feature_name,
                    **self.env,
                }
            )
        )
        return ret

    @property
    def ayon_db_install_destination_expanded(self) -> pathlib.Path:
        LOGGER.debug(f"{self.env = }")
        if self.env is None:
            raise KeyError("`env` is `None`.")

        LOGGER.debug(f"Expanding {self.ayon_db_install_destination}...")
        ret = pathlib.Path(
            self.ayon_db_install_destination.expanduser()
            .as_posix()
            .format(
                **{
                    "FEATURE": self.feature_name,
                    **self.env,
                }
            )
        )
        return ret


CONFIG_STR = get_config_str(
    Config=Config,
)

