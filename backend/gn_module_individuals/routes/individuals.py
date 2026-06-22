from flask import jsonify, request
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, raiseload, selectinload

from geonature.core.gn_monitoring.models import TIndividuals
from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla_geo.utils import geojsonify

from .. import MODULE_CODE
from ..blueprint import blueprint
from ..models import IndividualDeployments
from ..models.individuals import (
    temporary_individual_date_expression,
    temporary_individual_geom_expression,
    temporary_individual_observers_expression,
)
from ..schemas.individuals import IndividualsListSchema, IndividualsMapSchema
from ..utils.errors import APIError, IndividualsErrorCode


def _parse_filters(args):
    return {
        "taxon": args.get("taxon", type=int),
        "active": args.get("active"),
        "bbox": args.get("bbox"),
    }


def _parse_bool(value):
    if value is None:
        return None
    normalized = value.lower()
    if normalized in ("true", "1", "yes", "y"):
        return True
    if normalized in ("false", "0", "no", "n"):
        return False
    raise APIError(IndividualsErrorCode.INVALID_FILTER, "Unsupported active value", 400)


def _parse_bbox(value):
    if not value:
        return None
    try:
        west, south, east, north = [float(part) for part in value.split(",")]
    except ValueError as exc:
        raise APIError(
            IndividualsErrorCode.INVALID_FILTER,
            "bbox must be formatted as west,south,east,north",
            400,
        ) from exc
    if west >= east or south >= north:
        raise APIError(
            IndividualsErrorCode.INVALID_FILTER, "bbox coordinates are inconsistent", 400
        )
    return west, south, east, north


def _apply_filters(query, filters):
    if filters["taxon"] is not None:
        query = query.where(TIndividuals.cd_nom == filters["taxon"])

    active = _parse_bool(filters["active"])
    if active is not None:
        query = query.where(TIndividuals.active == active)

    bbox = _parse_bbox(filters["bbox"])
    if bbox is not None:
        west, south, east, north = bbox
        envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)
        query = query.where(func.ST_Intersects(temporary_individual_geom_expression(), envelope))

    return query


def _parse_sort(args):
    direction = args.get("dir", "asc", type=str).lower()
    if direction not in ("asc", "desc"):
        raise APIError(IndividualsErrorCode.INVALID_FILTER, "dir must be asc or desc", 400)
    return {
        "prop": args.get("prop", "id_individual", type=str),
        "dir": direction,
    }


def _sort_expression(sort):
    sort_columns = {
        "id_individual": TIndividuals.id_individual,
        "individual_name": TIndividuals.individual_name,
        "cd_nom": TIndividuals.cd_nom,
        "active": TIndividuals.active,
        "id_digitiser": TIndividuals.id_digitiser,
        "meta_create_date": TIndividuals.meta_create_date,
        "meta_update_date": TIndividuals.meta_update_date,
        "last_obs_date": temporary_individual_date_expression(),
    }
    column = sort_columns.get(sort["prop"], TIndividuals.id_individual)
    expression = column.desc() if sort["dir"] == "desc" else column.asc()
    return expression, TIndividuals.id_individual.asc()


def _ordered(query, sort):
    return query.order_by(*_sort_expression(sort))


def _build_individuals_query(scope, filters, sort, *, eager_load=True):
    query = select(TIndividuals)
    if eager_load:
        query = query.options(
            raiseload("*"),
            joinedload(TIndividuals.taxon),
            *[joinedload(getattr(TIndividuals, n)) for n in TIndividuals.__nomenclatures__],
            joinedload(TIndividuals.digitiser),
            selectinload(TIndividuals.deployments).options(
                joinedload(IndividualDeployments.nomenclature_deployment_type),
                joinedload(IndividualDeployments.nomenclature_deployment_location),
            ),
        )
    query = _apply_filters(query, filters)
    query = TIndividuals.filter_by_scope(query, scope)
    return _ordered(query, sort)


def _assign_temporary_observation(individuals):
    """TEMPORAIRE : peuple geom/last_obs_date/last_obs_observers (voir models/individuals.py)."""
    if not individuals:
        return
    ids = [individual.id_individual for individual in individuals]
    rows = db.session.execute(
        select(
            TIndividuals.id_individual,
            temporary_individual_geom_expression().label("geom"),
            temporary_individual_date_expression().label("obs_date"),
            temporary_individual_observers_expression().label("observers"),
        ).where(TIndividuals.id_individual.in_(ids))
    )
    by_id = {row.id_individual: row for row in rows}
    for individual in individuals:
        row = by_id.get(individual.id_individual)
        individual.geom = row.geom if row else None
        individual.last_obs_date = row.obs_date if row else None
        individual.last_obs_observers = row.observers if row else None


def _pagination_payload(paginated, schema):
    return {
        "items": schema.dump(paginated.items),
        "total": paginated.total,
        "pages": paginated.pages,
        "page": paginated.page,
        "per_page": paginated.per_page,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev,
        "next_num": paginated.next_num,
        "prev_num": paginated.prev_num,
    }


@blueprint.route("/individuals/map", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
def individuals_map(scope):
    filters = _parse_filters(request.args)
    sort = {"prop": "id_individual", "dir": "asc"}

    query = _build_individuals_query(scope, filters, sort, eager_load=False).options(
        joinedload(TIndividuals.taxon),
    )
    individuals = db.session.scalars(query).unique().all()
    _assign_temporary_observation(individuals)

    schema = IndividualsMapSchema(
        many=True,
        as_geojson=True,
        only=(
            "id_individual",
            "individual_name",
            "geom",
            "nom_vern",
            "last_observation",
        ),
    )
    return geojsonify(schema.dump(individuals))


@blueprint.route("/individuals", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
def list_individuals(scope):
    filters = _parse_filters(request.args)
    sort = _parse_sort(request.args)
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    query = _build_individuals_query(scope, filters, sort)
    schema = IndividualsListSchema(
        many=True, only=["+taxref", *[f"+{n}" for n in TIndividuals.__nomenclatures__]]
    )

    if page is not None and per_page is not None:
        paginated = db.paginate(query, page=page, per_page=per_page)
        _assign_temporary_observation(paginated.items)
        return jsonify(_pagination_payload(paginated, schema))

    individuals = db.session.scalars(query).unique().all()
    _assign_temporary_observation(individuals)
    return jsonify({"items": schema.dump(individuals)})


@blueprint.route("/individuals/<int:id_individual>/page", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
def individual_page(scope, id_individual):
    filters = _parse_filters(request.args)
    sort = _parse_sort(request.args)
    per_page = request.args.get("per_page", 20, type=int)
    if per_page < 1:
        raise APIError(IndividualsErrorCode.INVALID_FILTER, "per_page must be greater than 0", 400)

    query = _build_individuals_query(scope, filters, sort, eager_load=False)
    ranked = (
        query.with_only_columns(
            TIndividuals.id_individual,
            func.row_number().over(order_by=_sort_expression(sort)).label("rank"),
        )
        .order_by(None)
        .subquery()
    )

    rank = db.session.scalar(select(ranked.c.rank).where(ranked.c.id_individual == id_individual))
    if rank is None:
        raise APIError(
            IndividualsErrorCode.INDIVIDUAL_NOT_FOUND,
            "Individual not found in current filtered result",
            404,
            params={"id": id_individual},
        )

    return jsonify(
        {
            "id_individual": id_individual,
            "rank": rank,
            "page": ((rank - 1) // per_page) + 1,
            "per_page": per_page,
        }
    )
