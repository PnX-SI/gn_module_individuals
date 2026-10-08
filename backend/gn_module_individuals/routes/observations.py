"""Synthese observations linked to an individual.

Temporary routes: /synthese/for_web does not return the individual name and
cannot filter on "has an individual". They will be replaced by the new
synthese routes in a next GeoNature version.

Same logic as the individuals routes: GET /observations for the datatable
(paginated, sorted), GET /observations/geometry for the map.
"""

import datetime
import json

from flask import request, g, jsonify
from sqlalchemy import func, select
from werkzeug.exceptions import BadRequest, Forbidden

from geonature.core.gn_monitoring.models import TIndividuals
from geonature.core.gn_permissions.decorators import permissions_required
from geonature.core.gn_synthese.models import VSyntheseForWebApp
from geonature.core.gn_synthese.synthese_config import MANDATORY_COLUMNS
from geonature.core.gn_synthese.utils.blurring import split_blurring_precise_permissions
from geonature.core.gn_synthese.utils.query_select_sqla import SyntheseQuery
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from ..blueprint import blueprint
from .utils import pagination_payload, parse_sort

# Properties of the map features (the datatable gets OBSERVATIONS.LIST_COLUMNS)
MAP_COLUMNS = ["id_synthese", "nom_vern_or_lb_nom", "date_min", "observers"]


def _individual_name_expression():
    return (
        select(TIndividuals.individual_name)
        .where(TIndividuals.id_individual == VSyntheseForWebApp.id_individual)
        .scalar_subquery()
    )


def _column_expressions(column_names):
    """Return {name: SQL expression} for the given VSyntheseForWebApp columns,
    plus id_individual and individual_name."""
    expressions = {}
    for column in dict.fromkeys([*column_names, "id_individual"]):  # dedupe, keep order
        if column == "individual_name":
            expressions[column] = _individual_name_expression()
        elif column == "nom_vern_or_lb_nom":
            # Same computed column as /synthese/for_web
            expressions[column] = func.coalesce(
                func.nullif(VSyntheseForWebApp.nom_vern, ""), VSyntheseForWebApp.lb_nom
            )
        else:
            expression = getattr(VSyntheseForWebApp, column, None)
            if expression is None:
                raise BadRequest(f"Unknown observation column '{column}'")
            expressions[column] = expression

    if "individual_name" not in expressions:
        expressions["individual_name"] = _individual_name_expression()

    return expressions


def _json_object(expressions):
    return func.json_build_object(*[arg for item in expressions.items() for arg in item])


def _parse_date(value, name):
    if not value:
        return None
    try:
        datetime.datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise BadRequest(f"{name} must be formatted as YYYY-MM-DD") from exc
    return value


def _parse_filters(args):
    """Split the query string into synthese filters (SyntheseQuery format)
    and the module's own filters."""
    synthese_filters = {
        "individuals": args.getlist("id_individual", type=int),
        "id_dataset": args.getlist("id_dataset", type=int),
        "cd_nom": args.get("cd_nom", type=int),
        "date_min": _parse_date(args.get("date_min"), "date_min"),
        "date_max": _parse_date(args.get("date_max"), "date_max"),
    }
    # SyntheseQuery applies every key it gets: drop the empty ones
    synthese_filters = {k: v for k, v in synthese_filters.items() if v not in (None, [])}
    return synthese_filters, {"individual_name": args.get("individual_name")}


def _filtered_ids_query(permissions, synthese_filters, module_filters):
    """id_synthese of the observations linked to an individual, filtered by the
    synthese filters and the user's SYNTHESE permission scope.

    Kept apart from the selected columns and the sort: some synthese filters
    join other tables (areas, observers...) and could duplicate rows.
    """
    query = select(VSyntheseForWebApp.id_synthese).where(
        VSyntheseForWebApp.the_geom_4326.isnot(None),
        VSyntheseForWebApp.id_individual.isnot(None),
    )
    if module_filters["individual_name"]:
        query = query.where(
            _individual_name_expression().ilike(f"%{module_filters['individual_name']}%")
        )
    synthese_query = SyntheseQuery(VSyntheseForWebApp, query, synthese_filters)
    synthese_query.apply_all_filters(g.current_user, permissions)
    return synthese_query.build_query()


def _observations(expressions, ids):
    """Columns of the given observations as dicts, in the order of ids."""
    if not ids:
        return []
    rows = db.session.execute(
        select(VSyntheseForWebApp.id_synthese, _json_object(expressions)).where(
            VSyntheseForWebApp.id_synthese.in_(ids)
        )
    )
    by_id = dict(rows.all())
    return [by_id[id_synthese] for id_synthese in ids]


def _check_no_blurring(permissions):
    blurring_permissions, _ = split_blurring_precise_permissions(permissions)
    if blurring_permissions:
        raise Forbidden(
            "Observations with blurred geometries (sensitivity filter) are not supported "
            "by this module"
        )


@blueprint.route("/observations", methods=["GET"])
@permissions_required("R", module_code="SYNTHESE")
@json_resp
def list_observations(permissions):
    """
    List the synthese observations linked to an individual

    .. :quickref: Observations;

    Requires the R permission on the SYNTHESE module, restricted to its scope.
    Data blurring is not supported: a user whose SYNTHESE permissions have a
    sensitivity filter gets a 403 rather than precise geometries.

    :query int id_individual: filter on an individual (repeatable)
    :query string individual_name: filter on the individual name (partial match)
    :query int cd_nom: filter on the taxon
    :query int id_dataset: filter on a dataset (repeatable)
    :query string date_min: observations from this date (``YYYY-MM-DD``)
    :query string date_max: observations until this date (``YYYY-MM-DD``)
    :query string prop: column to sort on (default: date_min)
    :query string dir: sort direction, ``asc`` or ``desc`` (default: desc)
    :query int page: page number, requires per_page to enable pagination
    :query int per_page: page size, requires page to enable pagination

    :returns: the OBSERVATIONS.LIST_COLUMNS of the observations, with their
        id_individual and individual_name, wrapped in a pagination envelope
        (``items``, ``total``, ``pages``, ``has_next``...) when page and
        per_page are provided. Bounded by OBSERVATIONS.NB_MAX_OBS otherwise.
    :rtype: dict
    """
    _check_no_blurring(permissions)
    entity_config = blueprint.config["OBSERVATIONS"]
    synthese_filters, module_filters = _parse_filters(request.args)
    sort = parse_sort(request.args, "date_min")
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    expressions = _column_expressions([*MANDATORY_COLUMNS, *entity_config["LIST_COLUMNS"]])
    sort_column = expressions.get(sort["prop"], VSyntheseForWebApp.date_min)
    # Sorted ids only: db.paginate() applies unique() on the rows, which can't be
    # done on the json_build_object dicts. Their columns are fetched afterwards.
    ids_query = (
        select(VSyntheseForWebApp.id_synthese)
        .where(
            VSyntheseForWebApp.id_synthese.in_(
                _filtered_ids_query(permissions, synthese_filters, module_filters)
            )
        )
        .order_by(
            sort_column.desc() if sort["dir"] == "desc" else sort_column.asc(),
            # Tie-breaker for a stable pagination
            VSyntheseForWebApp.id_synthese.desc(),
        )
    )

    if page is not None and per_page is not None:
        paginated = db.paginate(ids_query, page=page, per_page=per_page, error_out=False)
        return pagination_payload(paginated, _observations(expressions, paginated.items), sort)

    ids = db.session.scalars(ids_query.limit(entity_config["NB_MAX_OBS"])).all()
    return {"items": _observations(expressions, ids), "prop": sort["prop"], "dir": sort["dir"]}


@blueprint.route("/observations/geometry", methods=["GET"])
@permissions_required("R", module_code="SYNTHESE")
def observations_geometry(permissions):
    """
    List the synthese observations linked to an individual, as GeoJSON points

    .. :quickref: Observations;

    Same permissions and filters as :func:`list_observations`. The most recent
    observations first, bounded by OBSERVATIONS.NB_MAX_OBS.

    :returns: a GeoJSON FeatureCollection of observations
    :rtype: dict<FeatureCollection>
    """
    _check_no_blurring(permissions)
    entity_config = blueprint.config["OBSERVATIONS"]
    synthese_filters, module_filters = _parse_filters(request.args)

    query = (
        select(
            VSyntheseForWebApp.id_synthese,
            # GeoJSON produced by PostGIS, as for /individuals/geometry
            VSyntheseForWebApp.st_asgeojson,
            _json_object(_column_expressions(MAP_COLUMNS)),
        )
        .where(
            VSyntheseForWebApp.id_synthese.in_(
                _filtered_ids_query(permissions, synthese_filters, module_filters)
            )
        )
        .order_by(VSyntheseForWebApp.date_min.desc(), VSyntheseForWebApp.id_synthese.desc())
        .limit(entity_config["NB_MAX_OBS"])
    )

    features = [
        {
            "type": "Feature",
            "id": id_synthese,
            "geometry": json.loads(geojson),
            "properties": properties,
        }
        for id_synthese, geojson, properties in db.session.execute(query)
    ]
    return jsonify({"type": "FeatureCollection", "features": features})
