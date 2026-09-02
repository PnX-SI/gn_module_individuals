from marshmallow import fields, validates, validates_schema, ValidationError
from utils_flask_sqla.schema import SmartRelationshipsMixin
from utils_flask_sqla_geo.schema import GeoAlchemyAutoSchema, GeoModelConverter, GeometryField
from datetime import datetime

from apptax.taxonomie.models import Taxref
from geonature.utils.env import db, ma
from geonature.utils.schema import CruvedSchemaMixin
from geonature.core.gn_permissions.tools import get_scopes_by_action
from pypnnomenclature.utils import NomenclaturesConverter
from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.schemas import NomenclatureSchema
from pypnusershub.schemas import UserSchema
from geonature.core.gn_monitoring.models import TIndividuals
from geonature.core.gn_commons.models import TAdditionalFields

from .. import MODULE_CODE
from ..models import TrackingDevices, IndividualDeployments
from .utils import get_label, is_nomenclature_of_type
from ..utils.errors import APIError, ApiErrorCode


class IndividualsMapConverter(NomenclaturesConverter, GeoModelConverter):
    pass


class IndividualsMapSchema(SmartRelationshipsMixin, GeoAlchemyAutoSchema):
    class Meta:
        model = TIndividuals
        include_fk = False
        load_instance = True
        sqla_session = db.session
        feature_id = "id_individual"
        feature_geometry = "geom"
        model_converter = IndividualsMapConverter

    geom = GeometryField(metadata={"exclude": True}, dump_only=True)
    taxref_nom_vern = fields.Method("get_taxref_nom_vern", dump_only=True)
    last_observation_date = fields.Method("get_last_observation_date", dump_only=True)
    last_observation_observers_name = fields.Method(
        "get_last_observation_observers_name", dump_only=True
    )

    def get_taxref_nom_vern(self, obj):
        return obj.taxon.nom_vern if obj.taxon else None

    def get_last_observation_date(self, obj):
        if obj.last_obs_date is None:
            return None
        return obj.last_obs_date.strftime("%d-%m-%Y")

    def get_last_observation_observers_name(self, obj):
        return obj.last_obs_observers


class IndividualsBaseSchema(CruvedSchemaMixin, SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    """Raw columns genuinely shared by List and Detail. No relationships exposed,
    no computed field specific to either subclass."""

    class Meta:
        model = TIndividuals
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = False
        model_converter = NomenclaturesConverter

    __module_code__ = MODULE_CODE
    __object_code__ = "INDIVIDUALS"

    meta_create_date = fields.DateTime(format="%d-%m-%Y", dump_only=True)
    meta_update_date = fields.DateTime(format="%d-%m-%Y", dump_only=True, allow_none=True)


class IndividualsListSchema(IndividualsBaseSchema):
    """Adds only computed fields on top of the base: no relationships."""

    class Meta(IndividualsBaseSchema.Meta):
        # cd_nom is exposed renamed as taxref_cd_nom (below), not under its column name.
        exclude = ("uuid_individual", "cd_nom")

    __module_code__ = MODULE_CODE

    taxref_cd_nom = fields.Integer(attribute="cd_nom", dump_only=True)
    taxref_nom_vern = fields.Method("get_taxref_nom_vern", dump_only=True)
    taxref_lb_nom = fields.Method("get_taxref_lb_nom", dump_only=True)

    digitiser_name = fields.Method("get_digitiser_name", dump_only=True)
    nomenclature_sex_name = fields.Method("get_nomenclature_sex_name", dump_only=True)

    last_observation_date = fields.Method("get_last_observation_date", dump_only=True)
    last_observation_observers_name = fields.Method(
        "get_last_observation_observers_name", dump_only=True
    )

    deployed_devices = fields.Method("get_deployed_devices", dump_only=True)
    deployed_markings = fields.Method("get_deployed_markings", dump_only=True)

    def get_digitiser_name(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None

    def get_nomenclature_sex_name(self, obj):
        return get_label(obj.nomenclature_sex) if obj.nomenclature_sex else None

    def get_taxref_nom_vern(self, obj):
        return obj.taxon.nom_vern if obj.taxon else None

    def get_taxref_lb_nom(self, obj):
        return obj.taxon.lb_nom if obj.taxon else None

    def get_last_observation_date(self, obj):
        if obj.last_obs_date is None:
            return None
        return obj.last_obs_date.strftime("%d-%m-%Y")

    def get_last_observation_observers_name(self, obj):
        return obj.last_obs_observers

    def _active_deployments(self, obj):
        return sorted(
            (d for d in obj.deployments if d.removal_date is None),
            key=lambda d: d.install_date or datetime.min,
            reverse=True,
        )

    def get_deployed_devices(self, obj):
        devices = [d for d in self._active_deployments(obj) if d.id_tracking_device is not None]
        return {
            f"device_{i}": {
                "location_name": get_label(deployment.nomenclature_deployment_location),
                "name": (
                    get_label(deployment.tracking_device.nomenclature_device_type)
                    if deployment.tracking_device
                    else None
                ),
            }
            for i, deployment in enumerate(devices, start=1)
        }

    def get_deployed_markings(self, obj):
        markings = [d for d in self._active_deployments(obj) if d.id_tracking_device is None]
        return {
            f"marking_{i}": {
                "type_name": get_label(deployment.nomenclature_deployment_type),
                "location_name": get_label(deployment.nomenclature_deployment_location),
                "code": deployment.marking_code,
            }
            for i, deployment in enumerate(markings, start=1)
        }


class IndividualsDetailSchema(IndividualsBaseSchema):
    """All of the model's relationships, in addition to the base fields."""

    class Meta(IndividualsBaseSchema.Meta):
        # id_digitiser is replaced by the nested digitiser object (below).
        exclude = ("id_digitiser",)

    __module_code__ = MODULE_CODE

    nom_vern = fields.Method("get_nom_vern", dump_only=True)
    lb_nom = fields.Method("get_lb_nom", dump_only=True)
    nomenclature_sex = ma.Nested(NomenclatureSchema, dump_only=True)
    # The exclusion of max_level_profil avoid to load the relationship User.groups
    # thanks to that no error "Internal Server Error 'User.groups' is not available due to lazy='raise'"
    digitiser = ma.Nested(UserSchema(exclude=("max_level_profil",)), dump_only=True)
    deployments = fields.Method("get_deployments", dump_only=True)

    last_observation_date = fields.Method("get_last_observation_date", dump_only=True)
    last_observation_observers = fields.Method("get_last_observation_observers", dump_only=True)

    def get_nom_vern(self, obj):
        return obj.taxon.nom_vern if obj.taxon else None

    def get_lb_nom(self, obj):
        return obj.taxon.lb_nom if obj.taxon else None

    def get_last_observation_date(self, obj):
        if obj.last_obs_date is None:
            return None
        return obj.last_obs_date.strftime("%d-%m-%Y")

    def get_last_observation_observers(self, obj):
        return obj.last_obs_observers

    def get_deployments(self, obj):
        deployments = sorted(obj.deployments, key=lambda d: d.install_date or datetime.min, reverse=True)
        # individual_name is redundant here: we are already on that individual's page.
        return IndividualsDeploymentsSchema(many=True, exclude=("individual_name",)).dump(
            deployments
        )


class IndividualsWriteSchema(IndividualsBaseSchema):
    """Used to create/update an individual. id_digitiser is always set by the
    route from the current user, regardless of what is submitted here."""

    __module_code__ = MODULE_CODE
    __object_code__ = "INDIVIDUALS"

    uuid_individual = fields.UUID(dump_only=True)
    # id_digitiser is NOT NULL on the model but always set by the route from the
    # current user, so it must not be required at load time.
    id_digitiser = fields.Integer(dump_only=True)
    deployments = fields.Method("get_deployments", dump_only=True)

    # Serialization

    def get_deployments(self, obj):
        deployments = sorted(obj.deployments, key=lambda d: d.install_date, reverse=True)
        # individual_name is redundant here: we are already on that individual's page.
        return IndividualsDeploymentsSchema(many=True, exclude=("individual_name",)).dump(
            deployments
        )

    # Validators

    @validates("individual_name")
    def validate_individual_name(self, value, **kwargs):
        if not value or not value.strip():
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                "The individual name can't be empty",
                400,
            )
        return value

    @validates("cd_nom")
    def validate_cd_nom(self, value, **kwargs):
        exists = db.session.execute(db.select(Taxref).filter_by(cd_nom=value)).scalar_one_or_none()
        if exists is None:
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                f"The #{value} taxon (cd_nom) does not exist.",
                400,
            )
        return value

    @validates("id_nomenclature_sex")
    def validate_id_nomenclature_sex(self, value, **kwargs):
        if value is None:
            return value
        nomenclature = db.session.execute(
            db.select(TNomenclatures).filter_by(id_nomenclature=value)
        ).scalar_one_or_none()
        if nomenclature is None:
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                f"The #{value} nomenclature is not found in configured nomenclatures",
                400,
            )
        if not is_nomenclature_of_type(nomenclature, "SEXE"):
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                f"The #{value} nomenclature is not of the expected type (SEXE)",
                400,
            )
        return value

    @validates("additional_data")
    def validate_additional_data(self, value, **kwargs):
        if not value:
            return value
        authorized_fields = set(
            db.session.execute(
                db.select(TAdditionalFields.field_name).where(
                    TAdditionalFields.modules.any(module_code=MODULE_CODE)
                )
            ).scalars()
        )
        unknown_fields = set(value) - authorized_fields
        if unknown_fields:
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                f"The additional_data field(s) {', '.join(sorted(unknown_fields))} "
                "are not authorized for this module.",
                400,
            )
        return value


class IndividualsDeploymentsSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IndividualDeployments
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        model_converter = NomenclaturesConverter
        feature_id = "id_deployment"

    id_deployment = ma.auto_field(dump_only=True)
    install_date = fields.DateTime(format="%Y-%m-%d", dump_only=True)
    removal_date = fields.DateTime(format="%Y-%m-%d", dump_only=True)
    meta_create_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    meta_update_date = fields.Date(format="%Y-%m-%d", dump_only=True)

    # nomenclature_deployment_type/location are Nested by default (auto-generated by
    # NomenclaturesConverter, SmartRelationshipsMixin excludes them). Include them via
    # only=[*[f"+{n}" for n in IndividualDeployments.__nomenclatures__]] when instantiating.
    individual_name = fields.Method("get_individual_name", dump_only=True)
    tracking_device_info = fields.Method("get_tracking_device", dump_only=True)
    name_digitiser = fields.Method("get_digitiser", dump_only=True)
    deployment_type_name = fields.Method("get_deployment_type_name", dump_only=True)
    deployment_location_name = fields.Method("get_deployment_location_name", dump_only=True)

    __module_code__ = MODULE_CODE

    # Validators

    @validates("id_individual")
    def validate_individual(self, value, **kwargs):
        if db.session.get(TIndividuals, value) is None:
            raise ValidationError(f"L'individu {value} n'existe pas.")
        return value

    @validates("id_tracking_device")
    def validate_tracking_device(self, value, **kwargs):
        if value is None:
            return value
        if db.session.get(TrackingDevices, value) is None:
            raise ValidationError(f"Le dispositif de suivi {value} n'existe pas.")
        return value

    @validates("id_nomenclature_deployment_type")
    def validate_nomenclature_deployment_type(self, value, **kwargs):
        nomenclature = db.session.get(TNomenclatures, value)
        if nomenclature is None:
            raise ValidationError(f"La nomenclature {value} (type de déploiement) n'existe pas.")
        if not is_nomenclature_of_type(nomenclature, "TYPE_MARQUAGE"):
            raise ValidationError(
                f"La nomenclature {value} n'est pas du type attendu (TYPE_MARQUAGE)."
            )
        return value

    @validates("id_nomenclature_deployment_location")
    def validate_nomenclature_deployment_location(self, value, **kwargs):
        nomenclature = db.session.get(TNomenclatures, value)
        if nomenclature is None:
            raise ValidationError(
                f"La nomenclature {value} (localisation du déploiement) n'existe pas."
            )
        if not is_nomenclature_of_type(nomenclature, "LOC_MARQUAGE"):
            raise ValidationError(
                f"La nomenclature {value} n'est pas du type attendu (LOC_MARQUAGE)."
            )
        return value

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """removal_date must be after install_date when both are present."""
        install = data.get("install_date")
        removal = data.get("removal_date")
        if install and removal and removal <= install:
            raise ValidationError(
                {"removal_date": ["removal_date doit être postérieure à install_date."]}
            )

    # Serialization

    def get_individual_name(self, obj):
        if obj.individual:
            name = obj.individual.individual_name
            if obj.individual.taxon and obj.individual.taxon.nom_vern:
                return f"{name} ({obj.individual.taxon.nom_vern})"
            return name
        return None

    def get_tracking_device(self, obj):
        if obj.tracking_device:
            return obj.tracking_device.device_label
        return None

    def get_digitiser(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None

    def get_deployment_type_name(self, obj):
        return get_label(obj.nomenclature_deployment_type)

    def get_deployment_location_name(self, obj):
        return get_label(obj.nomenclature_deployment_location)


class IndividualsDeploymentsWriteSchema(IndividualsDeploymentsSchema):
    """Used to create/update a deployment under an individual's PUT"""

    __module_code__ = MODULE_CODE

    id_individual = fields.Integer(dump_only=True)
    id_digitiser = fields.Integer(dump_only=True)
    # Loadable here: the base schema marks them dump_only for read use.
    install_date = fields.DateTime(format="%Y-%m-%d")
    removal_date = fields.DateTime(format="%Y-%m-%d", allow_none=True, required=False)
