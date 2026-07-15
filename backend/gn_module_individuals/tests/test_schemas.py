import pytest
from datetime import datetime
from flask import g
from marshmallow import ValidationError
from sqlalchemy import select

from geonature.tests.utils import get_id_nomenclature
from geonature.utils.env import db
from pypnnomenclature.models import TNomenclatures

from gn_module_individuals.models import IndividualDeployments
from gn_module_individuals.schemas import (
    TrackingDevicesBaseSchema,
    TrackingDevicesDetailSchema,
    IndividualsDeploymentsSchema,
)
from gn_module_individuals.schemas.individuals import (
    IndividualsMapSchema,
    IndividualsListSchema,
    DeploymentsBaseSchema,
)


@pytest.mark.usefixtures("temporary_transaction")
class TestTrackingDevicesBaseSchema:

    # --- validators: None branches  --------------------------

    def test_validate_nomenclature_device_type_accepts_none(self, app):
        assert TrackingDevicesBaseSchema().validate_nomenclature_device_type(None) is None

    def test_validate_nomenclature_device_type_accepts_valid_id(self, app):
        valid_id = get_id_nomenclature("TYPE_DISPO_SUIVI", "1")
        assert TrackingDevicesBaseSchema().validate_nomenclature_device_type(valid_id) == valid_id

    def test_validate_referer_accepts_none(self, app):
        assert TrackingDevicesBaseSchema().validate_referer(None) is None

    def test_validate_referer_accepts_valid_id(self, app, users):
        user_id = users["admin_user"].id_role
        assert TrackingDevicesBaseSchema().validate_referer(user_id) == user_id

    def test_get_nomenclature_name_returns_label(self, app, devices):
        result = TrackingDevicesBaseSchema().get_nomenclature_name(devices[0])
        assert result is not None

    def test_get_digitiser_returns_name(self, app, devices):
        result = TrackingDevicesBaseSchema().get_digitiser_name(devices[0])
        assert result is not None

    def test_get_referer_returns_name(self, app, devices):
        result = TrackingDevicesBaseSchema().get_referer_name(devices[0])
        assert result is not None


@pytest.mark.usefixtures("temporary_transaction")
class TestTrackingDevicesDetailSchema:

    def test_get_nomenclature_name_returns_label(self, app, devices):
        assert TrackingDevicesDetailSchema().get_nomenclature_name(devices[0]) is not None

    def test_get_digitiser_returns_name(self, app, devices):
        assert TrackingDevicesDetailSchema().get_digitiser_name(devices[0]) is not None

    def test_get_referer_returns_name(self, app, devices):
        assert TrackingDevicesDetailSchema().get_referer_name(devices[0]) is not None

    def test_get_deployments_returns_list_with_individual_name(self, app, device_with_deployment):
        result = TrackingDevicesDetailSchema().get_deployments(device_with_deployment)
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["individual_name"] is not None


@pytest.mark.usefixtures("temporary_transaction")
class TestIndividualsDeploymentsSchema:

    # --- validate_individual --------------------------------

    def test_validate_individual_accepts_valid_id(self, app, individual):
        result = IndividualsDeploymentsSchema().validate_individual(individual.id_individual)
        assert result == individual.id_individual

    def test_validate_individual_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualsDeploymentsSchema().validate_individual(-1)

    # --- validate_tracking_device  ---------------------------

    def test_validate_tracking_device_accepts_none(self, app):
        assert IndividualsDeploymentsSchema().validate_tracking_device(None) is None

    def test_validate_tracking_device_accepts_valid_id(self, app, device):
        result = IndividualsDeploymentsSchema().validate_tracking_device(device.id_tracking_device)
        assert result == device.id_tracking_device

    def test_validate_tracking_device_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualsDeploymentsSchema().validate_tracking_device(-1)

    # --- validate_nomenclature_deployment_type  --------------

    def test_validate_nomenclature_deployment_type_rejects_none(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualsDeploymentsSchema().validate_nomenclature_deployment_type(None)

    def test_validate_nomenclature_deployment_type_accepts_valid_id(self, app):
        valid_id = db.session.scalar(db.select(TNomenclatures.id_nomenclature).limit(1))
        result = IndividualsDeploymentsSchema().validate_nomenclature_deployment_type(valid_id)
        assert result == valid_id

    def test_validate_nomenclature_deployment_type_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualsDeploymentsSchema().validate_nomenclature_deployment_type(-1)

    # --- validate_nomenclature_deployment_location ----------

    def test_validate_nomenclature_deployment_location_rejects_none(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualsDeploymentsSchema().validate_nomenclature_deployment_location(None)

    def test_validate_nomenclature_deployment_location_accepts_valid_id(self, app):
        valid_id = db.session.scalar(db.select(TNomenclatures.id_nomenclature).limit(1))
        result = IndividualsDeploymentsSchema().validate_nomenclature_deployment_location(valid_id)
        assert result == valid_id

    def test_validate_nomenclature_deployment_location_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualsDeploymentsSchema().validate_nomenclature_deployment_location(-1)

    # --- validate_dates -------------------------------------

    def test_validate_dates_rejects_removal_before_install(self, app):
        with pytest.raises(ValidationError):
            IndividualsDeploymentsSchema().validate_dates(
                {
                    "install_date": datetime(2024, 6, 1),
                    "removal_date": datetime(2024, 1, 1),
                }
            )

    def test_validate_dates_accepts_valid_order(self, app):
        IndividualsDeploymentsSchema().validate_dates(
            {
                "install_date": datetime(2024, 1, 1),
                "removal_date": datetime(2024, 6, 1),
            }
        )

    # --- serialization methods --------------------------

    def test_get_tracking_device_returns_string(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        result = IndividualsDeploymentsSchema().get_tracking_device(deployment)
        assert result is not None

    def test_get_individual_name_returns_name(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        result = IndividualsDeploymentsSchema().get_individual_name(deployment)
        assert result is not None

    def test_dump_nomenclature_deployment_type_returns_nomenclature(
        self, app, device_with_deployment
    ):
        deployment = device_with_deployment.deployments[0]
        only = [f"+{n}" for n in IndividualDeployments.__nomenclatures__]
        dumped = IndividualsDeploymentsSchema(only=only).dump(deployment)
        assert dumped["nomenclature_deployment_type"]["cd_nomenclature"] == "4"

    def test_dump_nomenclature_deployment_location_returns_nomenclature(
        self, app, device_with_deployment
    ):
        deployment = device_with_deployment.deployments[0]
        only = [f"+{n}" for n in IndividualDeployments.__nomenclatures__]
        dumped = IndividualsDeploymentsSchema(only=only).dump(deployment)
        assert dumped["nomenclature_deployment_location"]["cd_nomenclature"] == "3"

    def test_get_digitiser_returns_none_when_unset(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        assert IndividualsDeploymentsSchema().get_digitiser(deployment) is None

    def test_has_instance_permission_scope_0_always_false(self, app, device):
        assert device.has_instance_permission(scope=0) is False

    def test_has_instance_permission_scope_3_always_true(self, app, device):
        assert device.has_instance_permission(scope=3) is True

    def test_has_instance_permission_scope_1_own_device(self, app, users, devices):
        # devices[2] has self_user as digitiser AND referer → access granted
        g.current_user = users["self_user"]
        assert devices[2].has_instance_permission(scope=1) is True

    def test_has_instance_permission_scope_1_other_device(self, app, users, devices):
        # devices[0] has admin_user as digitiser AND referer → self_user denied access
        g.current_user = users["self_user"]
        assert devices[0].has_instance_permission(scope=1) is False


# ===========================================================================
# IndividualsMapSchema
# ===========================================================================


@pytest.mark.usefixtures("temporary_transaction")
class TestIndividualsMapSchema:

    def test_get_nom_vern_returns_none_when_no_taxon(self, app, individual):
        individual.taxon = None
        result = IndividualsMapSchema().get_nom_vern(individual)
        assert result is None

    def test_get_nom_vern_returns_string_or_none(self, app, individual):
        # Taxon is loaded via fixture (valid cd_nom).
        # nom_vern may be None if the taxon has no vernacular name.
        result = IndividualsMapSchema().get_nom_vern(individual)
        assert result is None or isinstance(result, str)

    def test_get_last_observation_returns_none_when_no_date(self, app, individual):
        individual.last_obs_date = None
        assert IndividualsMapSchema().get_last_observation(individual) is None

    def test_get_last_observation_returns_dict_when_date_set(self, app, individual):
        individual.last_obs_date = datetime(2024, 6, 15)
        individual.last_obs_observers = "Alice Martin"
        result = IndividualsMapSchema().get_last_observation(individual)
        assert isinstance(result, dict)
        assert result["date"] == "15-06-2024"
        assert result["observateurs"] == "Alice Martin"

    def test_get_last_observation_date_format_dd_mm_yyyy(self, app, individual):
        individual.last_obs_date = datetime(2024, 1, 5)
        individual.last_obs_observers = None
        result = IndividualsMapSchema().get_last_observation(individual)
        assert result["date"] == "05-01-2024"

    def test_get_last_observation_observers_can_be_none(self, app, individual):
        individual.last_obs_date = datetime(2024, 6, 15)
        individual.last_obs_observers = None
        result = IndividualsMapSchema().get_last_observation(individual)
        assert result["observateurs"] is None


# ===========================================================================
# DeploymentsBaseSchema
# ===========================================================================


@pytest.mark.usefixtures("temporary_transaction")
class TestDeploymentsBaseSchema:

    def test_get_type_label_returns_nomenclature_label(
        self, app, device_with_deployment, individual
    ):
        deployment = individual.deployments[0]
        # device_with_deployment sets id_nomenclature_deployment_type to DISPO_SUIVI
        assert DeploymentsBaseSchema().get_type_label(deployment) == "Dispositif de suivi"

    def test_get_location_label_returns_nomenclature_label(
        self, app, device_with_deployment, individual
    ):
        deployment = individual.deployments[0]
        # device_with_deployment sets id_nomenclature_deployment_location to ENCOLURE
        assert DeploymentsBaseSchema().get_location_label(deployment) == "Encolure"

    def test_get_type_label_returns_string_when_nomenclature_set(
        self, app, device_with_deployment, individual
    ):
        deployment = individual.deployments[0]
        nomenclature = db.session.scalar(
            select(TNomenclatures).where(TNomenclatures.label_default.isnot(None)).limit(1)
        )
        deployment.nomenclature_deployment_type = nomenclature
        result = DeploymentsBaseSchema().get_type_label(deployment)
        assert isinstance(result, str)

    def test_get_location_label_returns_string_when_nomenclature_set(
        self, app, device_with_deployment, individual
    ):
        deployment = individual.deployments[0]
        nomenclature = db.session.scalar(
            select(TNomenclatures).where(TNomenclatures.label_default.isnot(None)).limit(1)
        )
        deployment.nomenclature_deployment_location = nomenclature
        result = DeploymentsBaseSchema().get_location_label(deployment)
        assert isinstance(result, str)


# ===========================================================================
# IndividualsListSchema
# ===========================================================================


@pytest.mark.usefixtures("temporary_transaction")
class TestIndividualsListSchema:

    def test_get_digitiser_name_returns_none_when_no_digitiser(self, app, individual):
        individual.digitiser = None
        result = IndividualsListSchema().get_digitiser_name(individual)
        assert result is None

    def test_get_digitiser_name_returns_full_name(self, app, individual):
        # individual fixture uses admin_user as digitiser (lazy="joined")
        result = IndividualsListSchema().get_digitiser_name(individual)
        assert result is not None
        assert isinstance(result, str)

    def test_get_last_observation_returns_none_when_no_date(self, app, individual):
        individual.last_obs_date = None
        assert IndividualsListSchema().get_last_observation(individual) is None

    def test_get_last_observation_returns_dict_when_date_set(self, app, individual):
        individual.last_obs_date = datetime(2024, 6, 15)
        individual.last_obs_observers = "Bob Dupont"
        result = IndividualsListSchema().get_last_observation(individual)
        assert isinstance(result, dict)
        assert result["date"] == "15-06-2024"
        assert result["observateurs"] == "Bob Dupont"

    def test_get_deployments_returns_empty_list_without_deployments(self, app, individual):
        # individual with no deployment → empty list
        result = IndividualsListSchema().get_deployments(individual)
        assert result == []

    def test_get_deployments_returns_list_with_deployment(
        self, app, device_with_deployment, individual
    ):
        result = IndividualsListSchema().get_deployments(individual)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_deployments_item_has_expected_keys(self, app, device_with_deployment, individual):
        result = IndividualsListSchema().get_deployments(individual)
        dep = result[0]
        for key in (
            "id_tracking_device",
            "marking_code",
            "install_date",
            "removal_date",
            "nomenclature_deployment_type",
            "nomenclature_deployment_location",
        ):
            assert key in dep, f"Missing key in serialized deployment: {key}"


# ===========================================================================
# TIndividuals.has_instance_permission
# ===========================================================================


@pytest.mark.usefixtures("temporary_transaction")
class TestTIndividualsPermission:

    def test_scope_0_always_false(self, app, individual):
        assert individual.has_instance_permission(scope=0) is False

    def test_scope_3_always_true(self, app, individual):
        assert individual.has_instance_permission(scope=3) is True

    def test_scope_1_own_individual(self, app, users, individuals):
        # individuals[2] has self_user as digitiser → access granted
        g.current_user = users["self_user"]
        assert individuals[2].has_instance_permission(scope=1) is True

    def test_scope_1_other_individual(self, app, users, individuals):
        # individuals[0] has admin_user as digitiser → self_user denied access
        g.current_user = users["self_user"]
        assert individuals[0].has_instance_permission(scope=1) is False

    def test_scope_2_own_individual_by_role(self, app, users, individuals):
        # scope=2: the digitiser always has access
        g.current_user = users["admin_user"]
        assert individuals[0].has_instance_permission(scope=2) is True

    def test_scope_2_grants_access_when_organisme_is_none(self, app, users, individuals):
        # In test fixtures, id_organisme is None for all users.
        # has_instance_permission checks `current_user.id_organisme in organism_actors`,
        # i.e. `None in [None]` → True: access granted even when digitiser differs.
        g.current_user = users["self_user"]
        assert individuals[0].has_instance_permission(scope=2) is True
