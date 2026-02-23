"""
Définition des routes du module export
"""

# import logging

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import Blueprint, request
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from . import MODULE_CODE

# A utiliser pour stocker les logs dans le fichier de log
# logger = logging.getLogger(__name__)
blueprint = Blueprint("individuals", __name__, cli_group="individuals")

## ########################################################################
## COLLECTION
## ########################################################################
