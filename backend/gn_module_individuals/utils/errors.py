from enum import Enum
from typing import Dict, Optional

from flask import jsonify


class DevicesErrorCode(str, Enum):
    """Error codes for tracking devices.

    Backend/frontend contract: the frontend uses the value as a translation
    key suffix (e.g. Individuals.ApiErrors.DeviceNotFound).
    """

    DEVICE_NOT_FOUND = "DeviceNotFound"
    DEVICE_HAS_DEPLOYMENTS = "DeviceHasDeployment"
    MISSING_JSON_BODY = "JsonBodyMissing"
    VALIDATION_ERROR = "ValidationError"
    INSUFFICIENT_PERMISSIONS = "InsufficientPermissions"


class IndividualsErrorCode(str, Enum):
    """Error codes for individuals.

    Backend/frontend contract: the frontend uses the value as a translation
    key suffix (e.g. Individuals.ApiErrors.IndividualNotFound).
    """

    INDIVIDUAL_NOT_FOUND = "IndividualNotFound"
    INVALID_FILTER = "InvalidFilter"


class APIError(Exception):
    """Structured exception producing {name, description}, as expected by MyCustomInterceptor.

    ``name`` is the machine code (e.g. DevicesErrorCode), used by the frontend as a
    translation key. ``description`` is the default English message, shown as-is if
    no translation is available.
    """

    def __init__(
        self,
        code: DevicesErrorCode,
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
