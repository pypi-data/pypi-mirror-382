from unittest.mock import MagicMock

import pytest
from sat.prtg import PRTGHandler


@pytest.fixture
def request_mocks():
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_session.get.return_value = mock_response
    return mock_session, mock_response


def test_successful_request(request_mocks):
    """Successful prtg response should return True"""
    mock_session, mock_response = request_mocks
    mock_response.status_code = 200

    prtg_handler = PRTGHandler("test-url", "test-guid", mock_session)
    result = prtg_handler.metric_to_prtg(value=1)

    assert result is True


def test_failed_request(request_mocks):
    """
    A failed request should return false and log a warning

    A failed request is any status code not equal to 200
    """
    mock_session, mock_response = request_mocks
    mock_response.status_code = 500

    prtg_handler = PRTGHandler("test-url", "test-guid", mock_session)
    result = prtg_handler.metric_to_prtg(value=1)

    assert result is False


def test_value_parameter(request_mocks):
    """The required value parameter should be used in the request params"""
    mock_session, mock_response = request_mocks
    mock_response.status_code = 200

    prtg_handler = PRTGHandler("test-url", "test-guid", mock_session)

    result = prtg_handler.metric_to_prtg(value=1)

    assert result is True
    assert mock_session.get.call_args.kwargs["params"] == {"value": 1}


def test_text_parameter(request_mocks):
    """Text argument should show up in params of sent request"""
    mock_session, mock_response = request_mocks
    mock_response.status_code = 200
    prtg_handler = PRTGHandler("test-url", "test-guid", mock_session)

    result = prtg_handler.metric_to_prtg(value=1, text="Test text string")

    assert result is True
    assert mock_session.get.call_args.kwargs["params"] == {"text": "Test text string", "value": 1}


def test_error_to_prtg(request_mocks):
    """Should be able to send an error to PRTG when an exception is caught"""
    mock_session, mock_response = request_mocks
    mock_response.status_code = 200
    prtg_handler = PRTGHandler("test-url", "test-guid", mock_session)

    result = prtg_handler.error_to_prtg()

    assert result is True


def test_error_to_prtg_with_message(request_mocks):
    """Should be able to send an error message to provide context to a handled error"""
    mock_session, mock_response = request_mocks
    mock_response.status_code = 200
    prtg_handler = PRTGHandler("test-url", "test-guid", mock_session)

    result = prtg_handler.error_to_prtg(text="Process failed because reasons")

    assert result is True
    assert mock_session.get.call_args.kwargs["params"] == {"text": "Process failed because reasons"}
