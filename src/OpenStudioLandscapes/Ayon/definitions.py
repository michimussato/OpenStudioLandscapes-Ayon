from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Ayon.assets
from OpenStudioLandscapes.engine.features.upstream_asset_specs import assets_external

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Ayon.assets],
)


defs = Definitions(
    assets=[
        *assets,
        *assets_external,
    ],
)
