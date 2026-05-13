"""
Définition des routes du module individus
"""

from flask import Blueprint

blueprint = Blueprint("individuals", __name__, cli_group="individuals")

from .routes import individuals, observations, captures, devices # noqa: F401
