from geonature.utils.env import db, ma
from marshmallow import fields, validates, validates_schema, ValidationError
from utils_flask_sqla.schema import SmartRelationshipsMixin

from geonature.utils.schema import CruvedSchemaMixin
from pypnnomenclature.utils import NomenclaturesConverter
from pypnnomenclature.models import TNomenclatures
from pypnusershub.schemas import UserSchema
from pypnusershub.db.models import User
from geonature.core.gn_monitoring.models import TIndividuals

from .. import MODULE_CODE
from ..models import TrackingDevices, IndividualDeployments
from .individuals import IndividualsDeploymentsSchema
from .utils import get_label


class DeploymentWriteSchema(IndividualsDeploymentsSchema):
    """Used to create/update a deployment, standalone, not related to an individual."""

    __module_code__ = MODULE_CODE

    id_digitiser = fields.Integer(dump_only=True)
    install_date = fields.DateTime(format="%Y-%m-%d")
    removal_date = fields.DateTime(format="%Y-%m-%d", allow_none=True, required=False)


class DeploymentSummarySchema(ma.Schema):
    id_individual = fields.Integer(dump_only=True)
    individual_name = fields.Method("get_individual_name", dump_only=True)
    install_date = fields.DateTime(format="%d-%m-%y", dump_only=True)
    removal_date = fields.DateTime(format="%d-%m-%y", dump_only=True)
    comment = fields.Method("get_comment", dump_only=True)

    __module_code__ = MODULE_CODE

    def get_individual_name(self, obj):
        if obj.individual:
            name = obj.individual.individual_name
            if obj.individual.taxon and obj.individual.taxon.nom_vern:
                return f"{name} ({obj.individual.taxon.nom_vern})"
            return name
        return None

    def get_comment(self, obj):
        if obj.comment:
            return obj.comment.replace("\n", "<br>")
        return None
