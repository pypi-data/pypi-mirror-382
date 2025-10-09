from enum import Enum

from pydantic import AfterValidator
from typing_extensions import Annotated


def validate_filled_string(value):
    if not value:
        raise ValueError("This string may not be empty")


ASSET_TYPES = Enum("ASSET_TYPES", ["Door", "Elevator"])

FILLED_STRING = Annotated[str, AfterValidator(validate_filled_string)]
