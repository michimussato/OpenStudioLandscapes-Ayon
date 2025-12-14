__all__ = [
    "ASSET_HEADER",
]

from OpenStudioLandscapes.Ayon import dist

# Todo
#  - [ ] fix this naive replacement logic
#  - [ ] AYONDB_INSIDE_CONTAINER
#        Reference? `kitsu_db_inside_container` for OpenStudioLandscapes-Kitsu
GROUP = dist.name.replace("-", "_")
KEY = [GROUP]

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
}
