from pydantic import UUID4, BaseModel

from sat.models.ccure.types import ASSET_TYPES, FILLED_STRING


class Asset(BaseModel):
    object_id: int
    name: FILLED_STRING
    guid: UUID4
    asset_type: ASSET_TYPES
