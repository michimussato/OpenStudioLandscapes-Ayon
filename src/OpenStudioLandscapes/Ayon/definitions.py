from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Ayon.assets
import OpenStudioLandscapes.Ayon.constants

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Ayon.assets],
)

constants = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Ayon.constants],
)


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
