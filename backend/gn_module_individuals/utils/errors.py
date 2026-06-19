from enum import Enum
from typing import Dict, Optional

from flask import jsonify


class DevicesErrorCode(str, Enum):
    """Nomenclature des codes d'erreur pour les dispositifs de suivi.

    Ces codes constituent le contrat entre backend et frontend :
    le frontend utilise la valeur comme suffixe de clé de traduction
    (ex. Individuals.ApiErrors.DEVICE_NOT_FOUND).
    """

    DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"
    DEVICE_HAS_DEPLOYMENTS = "DEVICE_HAS_DEPLOYMENTS"
    MISSING_JSON_BODY = "MISSING_JSON_BODY"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"


class APIError(Exception):
    """Exception structurée produisant {name, description} attendu par MyCustomInterceptor.

    Le champ ``name`` est le code machine (DeviceErrorCode), utilisé côté frontend
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
