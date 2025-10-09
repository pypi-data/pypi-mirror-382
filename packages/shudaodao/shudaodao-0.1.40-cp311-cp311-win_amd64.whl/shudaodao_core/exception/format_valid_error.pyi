from _typeshed import Incomplete
from fastapi.exceptions import RequestValidationError as RequestValidationError
from pydantic import ValidationError as ValidationError
from typing import Any

ERROR_MESSAGES: Incomplete

def format_request_validation_error(exc: RequestValidationError) -> list[dict[str, Any]]: ...
def format_pydantic_validation_error(exc: ValidationError) -> list[dict[str, Any]]: ...
