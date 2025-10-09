import pytest
from mm_result import Result
from pydantic import ValidationError

from mm_http import HttpResponse, TransportError, TransportErrorDetail


def test_to_result_ok_with_simple_value():
    """Test to_result_ok with a simple value."""
    response = HttpResponse(status_code=200, body='{"success": true}')
    result = response.to_result_ok(42)

    assert isinstance(result, Result)
    assert result.is_ok()
    assert result.value == 42
    assert result.extra and result.extra["status_code"] == 200


def test_to_result_ok_with_parsed_json():
    """Test to_result_ok with parsed JSON data."""
    response = HttpResponse(status_code=200, body='{"data": {"value": 123}}', headers={"content-type": "application/json"})
    parsed_value = response.parse_json("data.value")
    result = response.to_result_ok(parsed_value)

    assert result.is_ok()
    assert result.value == 123
    assert result.extra and result.extra["headers"]["content-type"] == "application/json"


def test_to_result_err_with_http_error():
    """Test to_result_err with TransportError."""
    response = HttpResponse(transport_error=TransportErrorDetail(type=TransportError.TIMEOUT, message="Request timed out"))
    result = response.to_result_err()

    assert result.is_err()
    assert result.error == TransportError.TIMEOUT
    assert result.extra and result.extra["transport_error"]["type"] == "timeout"
    assert result.extra["transport_error"]["message"] == "Request timed out"


def test_to_result_err_with_custom_error():
    """Test to_result_err with custom error message."""
    response = HttpResponse(status_code=404)
    result = response.to_result_err("Custom error message")

    assert result.is_err()
    assert result.error == "Custom error message"
    assert result.extra and result.extra["status_code"] == 404


def test_to_result_err_with_exception():
    """Test to_result_err with Exception object."""
    response = HttpResponse(transport_error=TransportErrorDetail(type=TransportError.CONNECTION, message="Connection error"))
    custom_exception = ValueError("Connection failed")
    result = response.to_result_err(custom_exception)

    assert result.is_err()
    assert result.error == "ValueError: Connection failed"
    assert result.extra and result.extra["transport_error"]["type"] == "connection"


def test_to_result_err_fallback():
    """Test to_result_err returns HTTP status code when no transport error is set."""
    response = HttpResponse(status_code=500)
    result = response.to_result_err()

    assert result.is_err()
    assert result.error == "HTTP 500"
    assert result.extra and result.extra["status_code"] == 500


def test_result_methods_preserve_response_data():
    """Test that both methods preserve all response data in extra."""
    response = HttpResponse(status_code=201, body='{"created": "item"}', headers={"location": "/items/123"})

    result = response.to_result_ok("success")

    expected_extra = {
        "status_code": 201,
        "body": '{"created": "item"}',
        "headers": {"location": "/items/123"},
        "transport_error": None,
    }

    assert result.extra == expected_extra


def test_integration_with_error_checking():
    """Test typical usage pattern with is_err() check."""
    # Success case
    response_ok = HttpResponse(status_code=200, body='{"value": 42}')

    result = response_ok.to_result_err() if response_ok.is_err() else response_ok.to_result_ok(response_ok.parse_json("value"))

    assert result.is_ok()
    assert result.value == 42

    # Error case
    response_err = HttpResponse(transport_error=TransportErrorDetail(type=TransportError.TIMEOUT, message="Timed out"))

    result = response_err.to_result_err() if response_err.is_err() else response_err.to_result_ok("should not happen")

    assert result.is_err()
    assert result.error == TransportError.TIMEOUT


def test_validation_cannot_have_both_states():
    """Test that validation prevents both HTTP response and transport error."""
    with pytest.raises(ValidationError, match="Cannot have both HTTP response and transport error"):
        HttpResponse(
            status_code=200,
            body="ok",
            transport_error=TransportErrorDetail(type=TransportError.TIMEOUT, message="timeout"),
        )


def test_validation_must_have_one_state():
    """Test that validation requires either HTTP response or transport error."""
    with pytest.raises(ValidationError, match="Must have either HTTP response or transport error"):
        HttpResponse()


def test_is_success():
    """Test is_success method."""
    # 2xx status
    assert HttpResponse(status_code=200).is_success()
    assert HttpResponse(status_code=201).is_success()
    assert HttpResponse(status_code=299).is_success()

    # Not 2xx
    assert not HttpResponse(status_code=199).is_success()
    assert not HttpResponse(status_code=300).is_success()
    assert not HttpResponse(status_code=404).is_success()
    assert not HttpResponse(status_code=500).is_success()

    # Transport error
    assert not HttpResponse(transport_error=TransportErrorDetail(type=TransportError.TIMEOUT, message="timeout")).is_success()
