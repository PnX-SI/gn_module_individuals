from enum import Enum
from typing import Dict, Optional

from flask import jsonify


class DevicesErrorCode(str, Enum):
    """Nomenclature des codes d'erreur pour les dispositifs de suivi.

    Ces codes constituent le contrat entre backend et frontend :
    le frontend utilise la valeur comme suffixe de clé de traduction
    (ex. Individuals.ApiErrors.DeviceNotFound).
    """

    DEVICE_NOT_FOUND = "DeviceNotFound"
    DEVICE_HAS_DEPLOYMENTS = "DeviceHasDeployment"
    MISSING_JSON_BODY = "JsonBodyMissing"
    VALIDATION_ERROR = "ValidationError"
    INSUFFICIENT_PERMISSIONS = "InsufficientPermissions"


class APIError(Exception):
    """Exception structurée produisant {name, description} attendu par MyCustomInterceptor.

    Le champ ``name`` est le code machine (DevicesErrorCode), utilisé côté frontend
    comme clé de traduction.  Le champ ``description`` est le message anglais par
    défaut, affiché tel quel si aucune traduction n'est disponible.
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
    """Sérialiseur Flask enregistré sur le blueprint individuals."""
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
