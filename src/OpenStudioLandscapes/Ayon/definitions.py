from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Ayon.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Ayon.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
