from enum import Enum
from typing import Dict, Optional

from flask import jsonify


class ApiErrorCode(str, Enum):
    """Error codes shared by all entities (devices, individuals, ...).

    Backend/frontend contract: the frontend uses the value as a generic
    translation key (e.g. Individuals.ApiErrors.NotFound), shared across
    entities rather than namespaced per entity.
    """

    NOT_FOUND = "NotFound"
    HAS_DEPLOYMENT = "HasDeployment"
    HAS_OBSERVATION = "HasObservation"
    INVALID_FILTER = "InvalidFilter"
    MISSING_JSON_BODY = "JsonBodyMissing"
    VALIDATION_ERROR = "ValidationError"
    INSUFFICIENT_PERMISSIONS = "InsufficientPermissions"


class APIError(Exception):
    """Structured exception producing {name, description}, as expected by MyCustomInterceptor.

    ``name`` is the machine code (e.g. ApiErrorCode), used by the frontend as a
    translation key. ``description`` is the default English message, shown as-is if
    no translation is available.
    """

    def __init__(
        self,
        code: ApiErrorCode,
        description: str,
        status: int = 400,
        params: Optional[Dict[str, object]] = None,
    ) -> None:
        self.error_code = code
        self.description = description
        self.status = status
        self.params = params or {}
        super().__init__(description)


def handle_error(error: APIError):
    """Flask error handler registered on the individuals blueprint."""
    return (
        jsonify(
            {
                "name": error.error_code.value,
                "description": error.description,
                "params": error.params,
            }
        ),
        error.status,
    )
