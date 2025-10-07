# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

from dataclasses import dataclass
from typing import Any, Optional, Tuple

from ._http_response import HttpResponse


class ApiError:
    _code: str
    _message: str
    _http_response: Optional[HttpResponse] = None

    def __init__(self, code: str, message: str) -> None:
        self._code = code
        self._message = message

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        if isinstance(other, ApiError):
            return self.code == other.code and self.message == other.message
        return False

    @property
    def code(self) -> str:
        if self._http_response is not None:
            return f"HTTP {self._http_response.code}"
        return self._code

    @property
    def message(self) -> str:
        if self._http_response is not None:
            if self._http_response.content_type and self._http_response.content:
                return (
                    self._http_response.content_type
                    + "\n"
                    + str(self._http_response.content)
                )
            elif self._http_response.content_type:
                return self._http_response.content_type
            elif self._http_response.content:
                return str(self._http_response.content)
        return self._message

    @property
    def content_type(self) -> str:
        if self._http_response is not None:
            return self._http_response.content_type
        return ""

    @property
    def content(self) -> Any:
        if self._http_response is not None:
            return self._http_response.content
        return None

    @property
    def is_available(self) -> bool:
        return bool(self.code) or bool(self.message)

    def to_exception(self) -> Optional[Exception]:
        return Exception(f"{self.code} {self.message}") if self.is_available else None

    @classmethod
    def create_from_http_response(cls, http_response: HttpResponse):
        instance = cls(code="", message="")
        instance._http_response = http_response
        return instance


@dataclass
class ApiResponse:
    is_success: bool = True
    status_code: str = ""
    content_type: str = ""
    error: Optional[ApiError] = None

    def raise_if_error(self) -> None:
        exc: Optional[Exception] = self.to_exception()
        if exc is not None:
            raise exc  # pylint: disable=raising-bad-type

    def to_exception(self) -> Optional[Exception]:
        if self.error is not None:
            return self.error.to_exception()
        if not self.is_success:
            return Exception(f"{self.status_code} unknown API error")
        return None

    def unpack(self) -> Tuple[Any, Any]:
        result, error = self
        return result, error

    def __iter__(self):
        yield None
        yield self.error


__all__ = [
    "ApiError",
    "ApiResponse",
]
