from __future__ import annotations

import enum
import json
from typing import Any

import pydash
from mm_result import Result
from pydantic import BaseModel, model_validator


@enum.unique
class TransportError(str, enum.Enum):
    TIMEOUT = "timeout"
    PROXY = "proxy"
    INVALID_URL = "invalid_url"
    CONNECTION = "connection"
    ERROR = "error"


class TransportErrorDetail(BaseModel):
    """Transport error with type and message."""

    type: TransportError
    message: str


class HttpResponse(BaseModel):
    """HTTP response with status, body, headers, and optional transport error."""

    status_code: int | None = None
    body: str | None = None
    headers: dict[str, str] | None = None
    transport_error: TransportErrorDetail | None = None

    @model_validator(mode="after")
    def validate_mutually_exclusive_states(self) -> HttpResponse:
        """Validate that response has either HTTP data or transport error, but not both."""
        has_http_response = self.status_code is not None
        has_transport_error = self.transport_error is not None

        if has_http_response and has_transport_error:
            msg = "Cannot have both HTTP response and transport error"
            raise ValueError(msg)

        if not has_http_response and not has_transport_error:
            msg = "Must have either HTTP response or transport error"
            raise ValueError(msg)

        return self

    def parse_json(self, path: str | None = None, none_on_error: bool = False) -> Any:  # noqa: ANN401
        """Parse JSON body and optionally extract value by path."""
        if self.body is None:
            if none_on_error:
                return None
            raise ValueError("Body is None")

        try:
            res = json.loads(self.body)
            return pydash.get(res, path, None) if path else res
        except json.JSONDecodeError:
            if none_on_error:
                return None
            raise

    def get_header(self, name: str) -> str | None:
        """Get header value (case-insensitive)."""
        if self.headers is None:
            return None
        name_lower = name.lower()
        for key, value in self.headers.items():
            if key.lower() == name_lower:
                return value
        return None

    def is_success(self) -> bool:
        """Check if response has 2xx status."""
        return self.status_code is not None and 200 <= self.status_code < 300

    def is_err(self) -> bool:
        """Check if response represents an error (has transport error or status >= 400)."""
        return self.transport_error is not None or (self.status_code is not None and self.status_code >= 400)

    def to_result_err[T](self, error: str | Exception | tuple[str, Exception] | None = None) -> Result[T]:
        """Create error Result[T] from HttpResponse with meaningful error message."""
        if error is not None:
            result_error = error
        elif self.transport_error is not None:
            result_error = self.transport_error.type
        elif self.status_code is not None:
            result_error = f"HTTP {self.status_code}"
        else:
            result_error = "error"
        return Result.err(result_error, extra=self.model_dump(mode="json"))

    def to_result_ok[T](self, value: T) -> Result[T]:
        """Create success Result[T] from HttpResponse with given value."""
        return Result.ok(value, extra=self.model_dump(mode="json"))

    @property
    def content_type(self) -> str | None:
        """Get Content-Type header value (case-insensitive)."""
        return self.get_header("content-type")
