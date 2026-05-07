from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Ayon.assets
from OpenStudioLandscapes.Ayon import (
    dist,
    LOGGER,
)

LOGGER.info(f"Loading {dist.name} assets...")

assets_base = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Ayon.assets],
)


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
