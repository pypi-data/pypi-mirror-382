import pydantic
import pytest
from sat.models.ccure.access import Clearance, Credential
from sat.models.ccure.assets import Asset


def test_valid_clearance(clearance):
    clr = clearance()
    assert Clearance(**clr)


def test_invalid_clearance_uuid(clearance):
    clr = clearance()
    clr["guid"] = "asldkfj-aslkdjf-aldlas-asldkj"
    with pytest.raises(pydantic.ValidationError) as ve:
        Clearance(**clr)
    assert "Input should be a valid UUID" in str(ve)


def test_invalid_clearance_name(clearance):
    clr = clearance()
    clr["name"] = ""
    with pytest.raises(pydantic.ValidationError) as ve:
        Clearance(**clr)
    assert "This string may not be empty" in str(ve)


def test_invalid_clearance_name_non_string(clearance):
    clr = clearance()
    clr["name"] = 12
    with pytest.raises(pydantic.ValidationError) as ve:
        Clearance(**clr)
    assert "Input should be a valid string" in str(ve)


def test_invalid_clearance_object_id(clearance):
    clr = clearance()
    clr["object_id"] = "1234b"
    with pytest.raises(pydantic.ValidationError) as ve:
        Clearance(**clr)
    assert "Input should be a valid integer" in str(ve)


def test_valid_credential(credential):
    cred = credential()
    assert Credential(**cred)


def test_invalid_credential_card_number(credential):
    cred = credential()
    cred["card_number"] = "1234567890b"
    with pytest.raises(pydantic.ValidationError) as ve:
        Credential(**cred)
    assert "Input should be a valid integer" in str(ve)


def test_invalid_credential_patron_id(credential):
    cred = credential()
    cred["patron_id"] = "1234567890b"
    with pytest.raises(pydantic.ValidationError) as ve:
        Credential(**cred)
    assert "Input should be a valid integer" in str(ve)


def test_asset_valid(asset):
    ast = asset()
    assert Asset(**ast)


def test_asset_invalid_name(asset):
    ast = asset()
    ast["name"] = ""
    with pytest.raises(pydantic.ValidationError) as ve:
        Asset(**ast)
    assert "This string may not be empty" in str(ve)


def test_asset_invalid_object_id(asset):
    ast = asset()
    ast["object_id"] = "1234b"
    with pytest.raises(pydantic.ValidationError) as ve:
        Asset(**ast)
    assert "Input should be a valid integer" in str(ve)


def test_asset_invalid_guid(asset):
    ast = asset()
    ast["guid"] = "asldkfj-aslkdjf-aldlas-asldkj"
    with pytest.raises(pydantic.ValidationError) as ve:
        Asset(**ast)
    assert "Input should be a valid UUID" in str(ve)


def test_asset_invalid_asset_type(asset):
    ast = asset()
    ast["asset_type"] = "Door"
    with pytest.raises(pydantic.ValidationError) as ve:
        Asset(**ast)
    assert "Input should be 1 or 2" in str(ve)
