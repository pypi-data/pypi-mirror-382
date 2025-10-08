import traceback
from typing import Union
from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
    ResponseValidationError,
)
from pydantic import ValidationError
from maleo.types.dict import StringToAnyDict
from maleo.types.any import SequenceOfAny


def extract_details(
    exc: Union[
        RequestValidationError,
        ResponseValidationError,
        ValidationError,
        HTTPException,
        Exception,
    ],
    *,
    include_traceback: bool = False,
) -> SequenceOfAny | StringToAnyDict:
    """
    Extracts structured details from an exception for logging, debugging, or API responses.

    Args:
        exc: The exception instance.
        include_traceback: Whether to include a formatted traceback string.

    Returns:
        A dictionary with the exception's type, message, args, and optionally traceback.
    """

    if isinstance(
        exc, (RequestValidationError, ResponseValidationError, ValidationError)
    ):
        return exc.errors()
    elif isinstance(exc, HTTPException):
        return {
            "exc_type": type(exc).__name__,
            "exc_data": {
                "status_code": exc.status_code,
                "detail": exc.detail,
                "headers": exc.headers,
            },
        }

    details: StringToAnyDict = {
        "exc_type": type(exc).__name__,
        "exc_data": {
            "message": str(exc),
            "args": exc.args,
        },
    }
    if include_traceback:
        details["traceback"] = traceback.format_exc()
    return details
