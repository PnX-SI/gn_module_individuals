import json

from flask import request, jsonify, g, make_response
from marshmallow import EXCLUDE, ValidationError

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.core.gn_monitoring.models import TIndividuals
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.schemas import NomenclatureSchema
from pypnusershub.db.models import User
from ..utils.errors import APIError, DevicesErrorCode

from .. import MODULE_CODE
from ..schemas import (
    TrackingDevicesDetailSchema,
    TrackingDevicesListSchema,
    TrackingDevicesWriteSchema,
)
from ..models import TrackingDevices, IndividualDeployments

from ..blueprint import blueprint


def _device_sort_columns():
    """Some `prop` values correspond to computed schema fields
    (nomenclature_device_type_name, digitiser_name, referer_name,
    last_individual_equipped_name) that don't exist on the model: map them
    here to an equivalent SQL expression (correlated subquery), same
    principle as occtax.repositories (SORT_COLUMNS + dispatch)."""
    return {
        "id_tracking_device": TrackingDevices.id_tracking_device,
        "id_nomenclature_device_type": TrackingDevices.id_nomenclature_device_type,
        "provider_name": TrackingDevices.provider_name,
        "provider_device_id": TrackingDevices.provider_device_id,
        "id_referer": TrackingDevices.id_referer,
        "comment": TrackingDevices.comment,
        "id_digitiser": TrackingDevices.id_digitiser,
        "meta_create_date": TrackingDevices.meta_create_date,
        "meta_update_date": TrackingDevices.meta_update_date,
        "nomenclature_device_type_name": (
            select(TNomenclatures.label_default)
            .where(TNomenclatures.id_nomenclature == TrackingDevices.id_nomenclature_device_type)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
        "digitiser_name": (
            select(func.concat(User.prenom_role, " ", User.nom_role))
            .where(User.id_role == TrackingDevices.id_digitiser)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
        "referer_name": (
            select(func.concat(User.prenom_role, " ", User.nom_role))
            .where(User.id_role == TrackingDevices.id_referer)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
        "last_individual_equipped_name": (
            select(TIndividuals.individual_name)
            .select_from(IndividualDeployments)
            .join(TIndividuals, TIndividuals.id_individual == IndividualDeployments.id_individual)
            .where(IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device)
            .order_by(IndividualDeployments.install_date.desc())
            .limit(1)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
    }


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def device(id_tracking_device, scope):
    """
    Return one tracking device

    .. :quickref: Devices;

    :param id_tracking_device: the id_tracking_device
    :type id_tracking_device: int

    :returns: a dict representing one tracking device with its nomenclatures,
        referer, digitiser and deployments
    :rtype: dict<TrackingDevices>
    """
    # Detail schema always exposes every relationship of the model.
    relationship_fields = list(TrackingDevices.__nomenclatures__) + ["referer", "digitiser"]
    schema = TrackingDevicesDetailSchema(only=["+cruved"] + relationship_fields)

    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments).joinedload(IndividualDeployments.individual),
        )
        .where(TrackingDevices.id_tracking_device == id_tracking_device)
    )

    device = db.session.execute(query).unique().scalar_one_or_none()

    if device is None:
        raise APIError(
            DevicesErrorCode.DEVICE_NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )
    if not device.has_instance_permission(scope):
        raise APIError(
            DevicesErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to read this device.",
            403,
        )
    return schema.dump(device)


@blueprint.route("/devices", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def list_devices(scope):
    """
    List tracking devices

    .. :quickref: Devices;

    :query int cd_nom: filter on the cd_nom of the last individual equipped
        with the device
    :query int id_nomenclature_device_type: filter on the device type
    :query string provider_name: filter on the provider name (partial match)
    :query int id_referer: filter on the referer role
    :query int page: page number, requires per_page to enable pagination
    :query int per_page: page size, requires page to enable pagination
    :query string prop: column to sort on (default: meta_create_date)
    :query string dir: sort direction, ``asc`` or ``desc`` (default: desc)

    :returns: `list<TrackingDevices>`, wrapped in a pagination envelope
        (``items``, ``total``, ``pages``, ``has_next``...) when page and
        per_page are provided
    :rtype: dict|list
    """
    # Scope not yet used -------------
    cd_nom = request.args.get("cd_nom", type=int)
    device_type = request.args.get("id_nomenclature_device_type", type=int)
    provider_name = request.args.get("provider_name", type=str)
    id_referer = request.args.get("id_referer", type=int)

    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    prop = request.args.get("prop", type=str, default="meta_create_date")
    dir = request.args.get("dir", type=str, default="desc")

    paginated = page is not None and per_page is not None

    schema = TrackingDevicesListSchema(only=["+cruved"])

    virtual_sort_cols = {
        "referer_name": (
            db.select(func.concat(User.prenom_role, " ", User.nom_role))
            .where(User.id_role == TrackingDevices.id_referer)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
        "nomenclature_device_type_name": (
            db.select(TNomenclatures.label_default)
            .where(TNomenclatures.id_nomenclature == TrackingDevices.id_nomenclature_device_type)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
        "last_individual_equipped_name": (
            db.select(TIndividuals.individual_name)
            .join(
                IndividualDeployments,
                IndividualDeployments.id_individual == TIndividuals.id_individual,
            )
            .where(IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device)
            .order_by(IndividualDeployments.install_date.desc())
            .limit(1)
            .correlate(TrackingDevices)
            .scalar_subquery()
        ),
    }

    sort_col = virtual_sort_cols.get(prop)
    if sort_col is None:
        sort_col = getattr(TrackingDevices, prop, None)
    if sort_col is None:
        sort_col = TrackingDevices.meta_create_date

    query = (
        db.select(TrackingDevices).options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments).joinedload(IndividualDeployments.individual),
        )
        # Requested sort, then id_tracking_device desc as a mandatory tie-breaker
        # (same convention as occtax.repositories) for stable pagination when
        # the sort column has ties.
        .order_by(
            sort_col.desc() if dir == "desc" else sort_col.asc(),
            TrackingDevices.id_tracking_device.desc(),
        )
    )

    if device_type is not None:
        query = query.where(TrackingDevices.id_nomenclature_device_type == device_type)
    if provider_name:
        query = query.where(TrackingDevices.provider_name.ilike(f"%{provider_name}%"))
    if id_referer is not None:
        query = query.where(TrackingDevices.id_referer == id_referer)
    if cd_nom is not None:
        query = query.where(
            db.select(IndividualDeployments.id_deployment)
            .join(TIndividuals, TIndividuals.id_individual == IndividualDeployments.id_individual)
            .where(
                IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device,
                TIndividuals.cd_nom == cd_nom,
            )
            .exists()
        )

    # Get only the items related to the scope
    query = TrackingDevices.filter_by_scope(query,scope)        

    if paginated:
        pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
        return {
            "items": schema.dump(pagination.items, many=True),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "prev_num": pagination.prev_num,
            "next_num": pagination.next_num,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    else:
        items = db.session.execute(query).unique().scalars().all()
        return schema.dump(items, many=True)


@blueprint.route("/devices", methods=["POST"])
@login_required
@permissions.check_cruved_scope(
    "C", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS_INDIVIDUALS"
)
@json_resp
def create_device(scope):
    """
    Post one new tracking device

    .. :quickref: Devices;

    Expects a JSON body matching ``TrackingDevicesWriteSchema``.

    :returns: the created device
    :rtype: dict<TrackingDevices>
    """
    data = request.get_json(silent=True)

    if not data:
        raise APIError(
            DevicesErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )
    
    schema = TrackingDevicesWriteSchema(unknown=EXCLUDE)
    try:
        device = schema.load(data)
    except ValidationError as e:
        raise APIError(
            DevicesErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    device.id_digitiser = g.current_user.id_role

    db.session.add(device)
    db.session.commit()

    return schema.dump(device), 201


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["PUT"])
@login_required
@permissions.check_cruved_scope(
    "U", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS_INDIVIDUALS"
)
@json_resp
def update_device(id_tracking_device, scope):
    """
    Update one tracking device

    .. :quickref: Devices;

    Expects a JSON body matching ``TrackingDevicesWriteSchema``.

    :param id_tracking_device: the id_tracking_device
    :type id_tracking_device: int

    :returns: the updated device
    :rtype: dict<TrackingDevices>
    """
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise APIError(
            DevicesErrorCode.DEVICE_NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )
    data = request.get_json(silent=True)

    if not data:
        raise APIError(
            DevicesErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )
    if not device.has_instance_permission(scope):
        raise APIError(
            DevicesErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to update device {id_tracking_device}.",
            403,
        )

    schema = TrackingDevicesWriteSchema(unknown=EXCLUDE)
    try:
        device = schema.load(data, instance=device)
    except ValidationError as e:
        raise APIError(
            DevicesErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    device.id_digitiser = g.current_user.id_role

    db.session.commit()

    return schema.dump(device), 200


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS_INDIVIDUALS"
)
def delete_device(id_tracking_device, scope):
    """
    Delete one tracking device

    .. :quickref: Devices;

    :param id_tracking_device: the id_tracking_device
    :type id_tracking_device: int

    :returns: empty response
    """
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise APIError(
            DevicesErrorCode.DEVICE_NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )

    if not device.has_instance_permission(scope):
        raise APIError(
            DevicesErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to delete device {id_tracking_device}.",
            403,
        )

    deployment_count = db.session.scalar(
        db.select(func.count())
        .select_from(IndividualDeployments)
        .where(IndividualDeployments.id_tracking_device == id_tracking_device)
    )
    if deployment_count:
        raise APIError(
            DevicesErrorCode.DEVICE_HAS_DEPLOYMENTS,
            "This device cannot be deleted because it is associated with deployments.",
            409,
            params={"id": id_tracking_device, "nb": deployment_count},
        )

    db.session.delete(device)
    db.session.commit()
    return make_response("", 204)
