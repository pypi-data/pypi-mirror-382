from pydantic import UUID4, BaseModel

from sat.models.ccure.types import FILLED_STRING


class Clearance(BaseModel):
    object_id: int
    guid: UUID4
    name: FILLED_STRING


class Credential(BaseModel):
    card_number: int
    patron_id: int
