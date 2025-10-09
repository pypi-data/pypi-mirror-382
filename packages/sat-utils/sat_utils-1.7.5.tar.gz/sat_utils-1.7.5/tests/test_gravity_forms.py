import os
from unittest import mock
from unittest.mock import patch

import pytest
from requests.exceptions import RequestException
from sat.gravity_forms import Entry, Form, GravityForms


@mock.patch.dict(
    os.environ,
    {
        "GRAVITY_FORMS_CONSUMER_KEY": "",
        "GRAVITY_FORMS_CONSUMER_SECRET": "secret",
        "GRAVITY_FORMS_BASE_URL": "https://baseurl.edu",
    },
)
def test_environment_variable_error_key():
    with pytest.raises(ValueError):
        GravityForms()


@mock.patch.dict(
    os.environ,
    {
        "GRAVITY_FORMS_CONSUMER_KEY": "your_key",
        "GRAVITY_FORMS_CONSUMER_SECRET": "",
        "GRAVITY_FORMS_BASE_URL": "https://baseurl.edu",
    },
)
def test_environment_variable_error_secret():
    with pytest.raises(ValueError):
        GravityForms()


@mock.patch.dict(
    os.environ,
    {
        "GRAVITY_FORMS_CONSUMER_KEY": "your_key",
        "GRAVITY_FORMS_CONSUMER_SECRET": "your_secret",
        "GRAVITY_FORMS_BASE_URL": "",
    },
)
def test_environment_variable_error_base_url():
    with pytest.raises(ValueError):
        GravityForms()


def test_request_exception_get():
    with patch("requests_oauthlib.OAuth1Session.get") as mock_get:
        mock_get.side_effect = RequestException("Simulated request exception.")
        gravity_forms = GravityForms(
            consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
        )
        try:
            _ = gravity_forms.get(
                "/forms/2/entries", params={"paging[current_page]": 1, "paging[page_size]": 5}
            )
            assert False
        except RequestException as e:
            assert str(e) == "Simulated request exception."


def test_get_forms_exception():
    with patch("requests_oauthlib.OAuth1Session.get") as mock_get:
        mock_get.side_effect = RequestException("Simulated request exception.")
        gravity_forms = GravityForms(
            consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
        )
        try:
            _ = gravity_forms.get_forms()
            assert False
        except RequestException as e:
            assert str(e) == "Simulated request exception."


def test_get_form_exception():
    with patch("requests_oauthlib.OAuth1Session.get") as mock_get:
        mock_get.side_effect = RequestException("Simulated request exception.")
        gravity_forms = GravityForms(
            consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
        )
        try:
            _ = gravity_forms.get_form("1234")
            assert False
        except RequestException as e:
            assert str(e) == "Simulated request exception."


def test_get_entries_exception():
    with patch("requests_oauthlib.OAuth1Session.get") as mock_get:
        mock_get.side_effect = RequestException("Simulated request exception.")
        gravity_forms = GravityForms(
            consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
        )
        try:
            _ = gravity_forms.get_entries()
            assert False
        except RequestException as e:
            assert str(e) == "Simulated request exception."


def test_get_entry_exception():
    with patch("requests_oauthlib.OAuth1Session.get") as mock_get:
        mock_get.side_effect = RequestException("Simulated request exception.")
        gravity_forms = GravityForms(
            consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
        )
        try:
            _ = gravity_forms.get_entry("1234")
            assert False
        except RequestException as e:
            assert str(e) == "Simulated request exception."


def test_field_filter_construct():
    expected_filter = (
        '{"field_filters": [{"key": "search_string", "value": "search_field", "operator": "="}]}'
    )
    gravity_forms = GravityForms(
        consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
    )
    result = gravity_forms.field_filters([("search_string", "search_field", "=")])
    assert expected_filter in result


def test_more_than_one_field_filter_construct():
    expected_filter = (
        '{"field_filters": [{"key": "search_string", "value": "search_field", "operator": "="},'
        ' {"key": "search_string1", "value": "search_field1", "operator": "contains"}]}'
    )
    gravity_forms = GravityForms(
        consumer_key="your_key", consumer_secret="your_secret", base_url="https://baseurl.edu"
    )
    result = gravity_forms.field_filters(
        [("search_string", "search_field", "="), ("search_string1", "search_field1", "contains")]
    )
    assert expected_filter in result


def test_create_form_model():
    form_data = {
        "id": "1",
        "title": "form title",
        "description": "form description",
        "is_active": True,
        "custom_field": "completely custom",
    }
    form = Form(**form_data)
    assert form.id == "1"
    assert form.title == "form title"
    assert form.description == "form description"
    assert form.is_active is True
    assert form.details == {"custom_field": "completely custom"}


def test_create_entry_model():
    entry_data = {
        "id": "1",
        "form_id": "1",
        "created_by": "yours truly",
        "status": "alive",
        "custom_field": "completely custom",
    }
    entry = Entry(**entry_data)
    assert entry.id == "1"
    assert entry.form_id == "1"
    assert entry.created_by == "yours truly"
    assert entry.status == "alive"
    assert entry.details == {"custom_field": "completely custom"}
