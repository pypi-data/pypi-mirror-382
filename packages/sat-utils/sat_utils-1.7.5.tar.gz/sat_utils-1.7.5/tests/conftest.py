from uuid import uuid4

import pytest
from sat.models.ccure.types import ASSET_TYPES


@pytest.fixture
def clearance():
    def _clearance(multiple: int = None):
        clearance = {
            "name": "John Doe",
            "object_id": 1234,
            "guid": str(uuid4()),
        }
        if multiple:
            return [clearance for _ in range(multiple)]
        else:
            return clearance

    return _clearance


@pytest.fixture
def credential():
    def _credential(multiple: int = None):
        credential = {
            "card_number": 1234567890,
            "patron_id": 1234567890,
        }
        if multiple:
            return [credential for _ in range(multiple)]
        else:
            return credential

    return _credential


@pytest.fixture
def asset():
    def _asset(multiple: int = None):
        asset = {
            "name": "Asset Name",
            "object_id": 1234,
            "guid": str(uuid4()),
            "asset_type": ASSET_TYPES.Door,
        }
        if multiple:
            return [asset for _ in range(multiple)]
        else:
            return asset

    return _asset
