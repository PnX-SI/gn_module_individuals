import pytest
from datetime import datetime
from flask import g
from marshmallow import ValidationError

from geonature.tests.utils import get_id_nomenclature
from geonature.utils.env import db
from pypnnomenclature.models import TNomenclatures

from gn_module_individuals.schemas import (
    TrackingDevicesSchema,
    TrackingDeviceDetailSchema,
    IndividualDeploymentsSchema,
)


@pytest.mark.usefixtures("temporary_transaction")
class TestTrackingDevicesSchema:

    # --- validators : branches None  --------------------------

    def test_validate_nomenclature_device_type_accepts_none(self, app):
        assert TrackingDevicesSchema().validate_nomenclature_device_type(None) is None

    def test_validate_nomenclature_device_type_accepts_valid_id(self, app):
        valid_id = get_id_nomenclature("TYPE_DISPO_SUIVI", "1")
        assert TrackingDevicesSchema().validate_nomenclature_device_type(valid_id) == valid_id

    def test_validate_referer_accepts_none(self, app):
        assert TrackingDevicesSchema().validate_referer(None) is None

    def test_validate_referer_accepts_valid_id(self, app, users):
        user_id = users["admin_user"].id_role
        assert TrackingDevicesSchema().validate_referer(user_id) == user_id


    def test_get_nomenclature_name_returns_label(self, app, devices):
        result = TrackingDevicesSchema().get_nomenclature_name(devices[0])
        assert result is not None

    def test_get_digitiser_returns_name(self, app, devices):
        result = TrackingDevicesSchema().get_digitiser(devices[0])
        assert result is not None

    def test_get_referer_returns_name(self, app, devices):
        result = TrackingDevicesSchema().get_referer(devices[0])
        assert result is not None



@pytest.mark.usefixtures("temporary_transaction")
class TestTrackingDeviceDetailSchema:

    def test_get_nomenclature_name_returns_label(self, app, devices):
        assert TrackingDeviceDetailSchema().get_nomenclature_name(devices[0]) is not None

    def test_get_digitiser_returns_name(self, app, devices):
        assert TrackingDeviceDetailSchema().get_digitiser(devices[0]) is not None

    def test_get_referer_returns_name(self, app, devices):
        assert TrackingDeviceDetailSchema().get_referer(devices[0]) is not None

    def test_get_deployments_returns_list_with_individual_name(self, app, device_with_deployment):
        result = TrackingDeviceDetailSchema().get_deployments(device_with_deployment)
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]["individual_name"] is not None


@pytest.mark.usefixtures("temporary_transaction")
class TestIndividualDeploymentsSchema:

    # --- validate_individual --------------------------------

    def test_validate_individual_accepts_valid_id(self, app, individual):
        result = IndividualDeploymentsSchema().validate_individual(individual.id_individual)
        assert result == individual.id_individual

    def test_validate_individual_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualDeploymentsSchema().validate_individual(-1)

    # --- validate_tracking_device  ---------------------------

    def test_validate_tracking_device_accepts_valid_id(self, app, device):
        result = IndividualDeploymentsSchema().validate_tracking_device(device.id_tracking_device)
        assert result == device.id_tracking_device

    def test_validate_tracking_device_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualDeploymentsSchema().validate_tracking_device(-1)

    # --- validate_nomenclature_deployment_type  --------------

    def test_validate_nomenclature_deployment_type_accepts_none(self, app):
        assert IndividualDeploymentsSchema().validate_nomenclature_deployment_type(None) is None

    def test_validate_nomenclature_deployment_type_accepts_valid_id(self, app):
        valid_id = db.session.scalar(db.select(TNomenclatures.id_nomenclature).limit(1))
        result = IndividualDeploymentsSchema().validate_nomenclature_deployment_type(valid_id)
        assert result == valid_id

    def test_validate_nomenclature_deployment_type_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualDeploymentsSchema().validate_nomenclature_deployment_type(-1)

    # --- validate_nomenclature_deployment_location ----------

    def test_validate_nomenclature_deployment_location_accepts_none(self, app):
        assert IndividualDeploymentsSchema().validate_nomenclature_deployment_location(None) is None

    def test_validate_nomenclature_deployment_location_accepts_valid_id(self, app):
        valid_id = db.session.scalar(db.select(TNomenclatures.id_nomenclature).limit(1))
        result = IndividualDeploymentsSchema().validate_nomenclature_deployment_location(valid_id)
        assert result == valid_id

    def test_validate_nomenclature_deployment_location_rejects_unknown_id(self, app):
        with pytest.raises(ValidationError, match="n'existe pas"):
            IndividualDeploymentsSchema().validate_nomenclature_deployment_location(-1)

    # --- validate_additional_data  ---------------------------

    def test_validate_additional_data_accepts_none(self, app):
        assert IndividualDeploymentsSchema().validate_additional_data(None) is None

    def test_validate_additional_data_rejects_non_dict(self, app):
        with pytest.raises(ValidationError, match="dict"):
            IndividualDeploymentsSchema().validate_additional_data("pas_un_dict")

    def test_validate_additional_data_rejects_forbidden_key(self, app):
        with pytest.raises(ValidationError, match="non autorisées"):
            IndividualDeploymentsSchema().validate_additional_data({"cle_interdite": "x"})

    def test_validate_additional_data_accepts_allowed_key(self, app):
        data = {"removal_reason": "fin de suivi"}
        assert IndividualDeploymentsSchema().validate_additional_data(data) == data

    # --- validate_dates -------------------------------------

    def test_validate_dates_rejects_removal_before_install(self, app):
        with pytest.raises(ValidationError):
            IndividualDeploymentsSchema().validate_dates(
                {
                    "install_date": datetime(2024, 6, 1),
                    "removal_date": datetime(2024, 1, 1),
                }
            )

    def test_validate_dates_accepts_valid_order(self, app):
        IndividualDeploymentsSchema().validate_dates(
            {
                "install_date": datetime(2024, 1, 1),
                "removal_date": datetime(2024, 6, 1),
            }
        )

    # --- méthodes de sérialisation --------------------------

    def test_get_tracking_device_returns_string(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        result = IndividualDeploymentsSchema().get_tracking_device(deployment)
        assert result is not None

    def test_get_individual_name_returns_name(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        result = IndividualDeploymentsSchema().get_individual_name(deployment)
        assert result is not None

    def test_get_deployment_type_returns_none_when_unset(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        assert IndividualDeploymentsSchema().get_deployment_type(deployment) is None

    def test_get_deployment_location_returns_none_when_unset(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        assert IndividualDeploymentsSchema().get_deployment_location(deployment) is None

    def test_get_digitiser_returns_none_when_unset(self, app, device_with_deployment):
        deployment = device_with_deployment.deployments[0]
        assert IndividualDeploymentsSchema().get_digitiser(deployment) is None


    def test_has_instance_permission_scope_0_always_false(self, app, device):
        assert device.has_instance_permission(scope=0) is False

    def test_has_instance_permission_scope_3_always_true(self, app, device):
        assert device.has_instance_permission(scope=3) is True

    def test_has_instance_permission_scope_1_own_device(self, app, users, devices):
        # devices[2] a self_user comme digitiseur ET référent → accès accordé
        g.current_user = users["self_user"]
        assert devices[2].has_instance_permission(scope=1) is True

    def test_has_instance_permission_scope_1_other_device(self, app, users, devices):
        # devices[0] a admin_user comme digitiseur ET référent → accès refusé pour self_user
        g.current_user = users["self_user"]
        assert devices[0].has_instance_permission(scope=1) is False
