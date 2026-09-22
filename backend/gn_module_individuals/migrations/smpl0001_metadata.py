"""Insert acquisition framework, datasets and additional fields 

Individuals-samples demo data.

Standalone "individuals-samples" branch: not applied by `geonature db
autoupgrade`, run manually (or in CI) with:
    geonature db upgrade individuals-samples@head

Revision ID: smpl0001_metadata
Revises:
Create Date: 2026-09-18 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "smpl0001_metadata"
down_revision = None
branch_labels = ("individuals-samples",)
depends_on = ("individuals",)

AF_NAME = "Cadre d'acquisition de test Individus"

# Datasets created for the demo, keyed by their dataset_shortname.
DATASETS = {
    "CAPTURES_BOUQUETIN_TEST": {
        "dataset_name": "Individus et captures bouquetins TEST",
        "dataset_desc": "Individus et captures (pose de marquage, mesures) des bouquetins de test",
        "module_code": "OCCTAX",
    },
    "CAPTURES_TETRAS_TEST": {
        "dataset_name": "Individus et captures tétras-lyre TEST",
        "dataset_desc": "Individus et captures (pose de marquage, mesures) des tétras-lyre de test",
        "module_code": "OCCTAX",
    },
    "OCCTAX_BOUQMARQ_TEST": {
        "dataset_name": "Occtax bouquetins marqués TEST",
        "dataset_desc": "Relevés Occtax (observations de terrain, suivi GPS) de test du module Individus",
        "module_code": "OCCTAX",
    },
}

# Additional fields created for the demo,
# widget/nomenclature-free fields resolve id_widget by widget_name so they
# don't depend on the numeric id assigned to each row by GeoNature core.
ADDITIONAL_FIELDS = {
    "birth_year": {
        "field_label": "Année de naissance",
        "description": "Année estimée de naissance",
        "widget_name": "number",
        "field_order": 1,
        "object_code": "INDIVIDUALS",
        "module_code": "INDIVIDUALS",
    },
    "death_date": {
        "field_label": "Date du décès",
        "description": "Date du décès présumée",
        "widget_name": "date",
        "field_order": 2,
        "object_code": "INDIVIDUALS",
        "module_code": "INDIVIDUALS",
    },
    "feather_obs": {
        "field_label": "Plumage",
        "description": "Observations du plumage",
        "widget_name": "text",
        "field_order": 3,
        "object_code": "INDIVIDUALS",
        "module_code": "INDIVIDUALS",
    },
    "capture_type": {
        "field_label": "Type de capture",
        "description": "Technique utilisée pour capturer l'individu",
        "widget_name": "select",
        "field_order": 1,
        "object_code": "OCCTAX_RELEVE",
        "module_code": "OCCTAX",
        "field_values": [
            {"label": "Cage", "value": "Cage"},
            {"label": "Filet", "value": "Filet"},
            {"label": "Téléanesthésie", "value": "Téléanesthésie"},
        ],
    },
    "capture_event": {
        "field_label": "Type d'évènement",
        "description": "Nature de l'évènement de capture",
        "widget_name": "select",
        "field_order": 2,
        "object_code": "OCCTAX_RELEVE",
        "module_code": "OCCTAX",
        "field_values": [
            {"label": "Capture", "value": "Capture"},
            {"label": "Recapture", "value": "Recapture"},
            {"label": "Cadavre", "value": "Cadavre"},
            {"label": "Accident de capture", "value": "Accident de capture"},
        ],
    },
    "weight": {
        "field_label": "Poids (kg)",
        "description": "Poids mesuré lors de la capture",
        "widget_name": "number",
        "quantitative": True,
        "unity": "kg",
        "field_order": 1,
        "object_code": "OCCTAX_OCCURRENCE",
        "module_code": "OCCTAX",
    },
    "horn_size": {
        "field_label": "Taille des cornes (cm)",
        "description": "Longueur des cornes mesurée lors de la capture",
        "widget_name": "number",
        "quantitative": True,
        "unity": "cm",
        "field_order": 2,
        "object_code": "OCCTAX_OCCURRENCE",
        "module_code": "OCCTAX",
    },
    "wing_size": {
        "field_label": "Taille de l'aile (cm)",
        "description": "Longueur de l'aile mesurée lors de la capture",
        "widget_name": "number",
        "quantitative": True,
        "unity": "cm",
        "field_order": 2,
        "object_code": "OCCTAX_OCCURRENCE",
        "module_code": "OCCTAX",
    },
    "with_young": {
        "field_label": "Femelle suitée",
        "description": "Présence d'un jeune accompagnant la femelle",
        "widget_name": "select",
        "field_order": 1,
        "object_code": "OCCTAX_OCCURRENCE",
        "module_code": "OCCTAX",
        "field_values": [
            {"label": "Certain", "value": "Certain"},
            {"label": "Probable", "value": "Probable"},
            {"label": "Indéterminé", "value": "Indéterminé"},
            {"label": "Absence", "value": "Absence"},
        ],
    },
}

# Which datasets each field is attached to (gn_commons.cor_field_dataset).
FIELD_DATASETS = {
    "birth_year": ("CAPTURES_BOUQUETIN_TEST", "CAPTURES_TETRAS_TEST"),
    "death_date": ("CAPTURES_BOUQUETIN_TEST", "CAPTURES_TETRAS_TEST"),
    "feather_obs": ("CAPTURES_BOUQUETIN_TEST", "CAPTURES_TETRAS_TEST"),
    "capture_type": ("CAPTURES_BOUQUETIN_TEST", "CAPTURES_TETRAS_TEST"),
    "capture_event": ("CAPTURES_BOUQUETIN_TEST", "CAPTURES_TETRAS_TEST"),
    "weight": ("CAPTURES_BOUQUETIN_TEST", "CAPTURES_TETRAS_TEST"),
    "horn_size": ("CAPTURES_BOUQUETIN_TEST",),
    "wing_size": ("CAPTURES_TETRAS_TEST",),
    "with_young": ("OCCTAX_BOUQMARQ_TEST",),
}

# Objects whose support_additional_fields flag we turn on. OCCTAX_RELEVE and
# OCCTAX_OCCURRENCE already default to true; INDIVIDUALS is our
# own object and defaults to false, so it's the only one we own the flip for.
SUPPORT_ADDITIONAL_FIELDS_OBJECTS = ("OCCTAX_RELEVE", "OCCTAX_OCCURRENCE", "INDIVIDUALS")


def upgrade():
    conn = op.get_bind()

    op.execute(sa.text("""
            INSERT INTO gn_meta.t_acquisition_frameworks (
                acquisition_framework_name, acquisition_framework_desc,
                acquisition_framework_start_date
            )
            SELECT :af_name, :af_name, CURRENT_DATE
            WHERE NOT EXISTS (
                SELECT 1 FROM gn_meta.t_acquisition_frameworks
                WHERE acquisition_framework_name = :af_name
            )
        """).bindparams(af_name=AF_NAME))

    op.execute(
        sa.text("""
            UPDATE gn_permissions.t_objects
            SET support_additional_fields = true
            WHERE code_object IN :object_codes
        """).bindparams(
            sa.bindparam("object_codes", value=SUPPORT_ADDITIONAL_FIELDS_OBJECTS, expanding=True)
        )
    )

    for shortname, dataset in DATASETS.items():
        op.execute(
            sa.text("""
                INSERT INTO gn_meta.t_datasets (
                    id_acquisition_framework, dataset_name, dataset_shortname, dataset_desc,
                    marine_domain, terrestrial_domain, id_digitizer
                )
                SELECT
                    af.id_acquisition_framework, :dataset_name, :shortname, :dataset_desc,
                    FALSE, TRUE, 4
                FROM gn_meta.t_acquisition_frameworks af
                WHERE af.acquisition_framework_name = :af_name
                    AND NOT EXISTS (
                        SELECT 1 FROM gn_meta.t_datasets WHERE dataset_shortname = :shortname
                    )
            """).bindparams(
                af_name=AF_NAME,
                shortname=shortname,
                dataset_name=dataset["dataset_name"],
                dataset_desc=dataset["dataset_desc"],
            )
        )
        op.execute(sa.text("""
                INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
                SELECT m.id_module, d.id_dataset
                FROM gn_commons.t_modules m, gn_meta.t_datasets d
                WHERE m.module_code = :module_code AND d.dataset_shortname = :shortname
            """).bindparams(module_code=dataset["module_code"], shortname=shortname))

    # CMR_BOUQUETIN monitoring dataset: only if the CMR_BOUQUETIN sub-module
    # has been installed beforehand via ./scripts/setup_cmr_demo.sh.
    cmr_installed = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
        )
    ).scalar()
    if cmr_installed:
        op.execute(sa.text("""
                INSERT INTO gn_meta.t_datasets (
                    id_acquisition_framework, dataset_name, dataset_shortname, dataset_desc,
                    marine_domain, terrestrial_domain, id_digitizer
                )
                SELECT
                    af.id_acquisition_framework, 'Suivi CMR bouquetins TEST', 'CMR_BOUQUETIN',
                    'Jeu de données du suivi capture-marquage-recapture des bouquetins du Parc national de la Vanoise',
                    FALSE, TRUE, 4
                FROM gn_meta.t_acquisition_frameworks af
                WHERE af.acquisition_framework_name = :af_name
                    AND NOT EXISTS (
                        SELECT 1 FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'
                    )
            """).bindparams(af_name=AF_NAME))
        op.execute(sa.text("""
            INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
            SELECT m.id_module, d.id_dataset
            FROM gn_commons.t_modules m, gn_meta.t_datasets d
            WHERE m.module_code = 'CMR_BOUQUETIN' AND d.dataset_shortname = 'CMR_BOUQUETIN'
        """))

    for field_name, field in ADDITIONAL_FIELDS.items():
        op.execute(
            sa.text("""
                INSERT INTO gn_commons.t_additional_fields (
                    field_name, field_label, required, description, id_widget,
                    quantitative, unity, field_values, exportable, field_order
                )
                SELECT
                    :field_name, :field_label, false, :description,
                    (SELECT id_widget FROM gn_commons.bib_widgets WHERE widget_name = :widget_name),
                    :quantitative, :unity, :field_values, true, :field_order
                WHERE NOT EXISTS (
                    SELECT 1 FROM gn_commons.t_additional_fields WHERE field_name = :field_name
                )
            """).bindparams(
                sa.bindparam("field_name", value=field_name),
                sa.bindparam("field_label", value=field["field_label"]),
                sa.bindparam("description", value=field["description"]),
                sa.bindparam("widget_name", value=field["widget_name"]),
                sa.bindparam("quantitative", value=field.get("quantitative", False)),
                sa.bindparam("unity", value=field.get("unity")),
                sa.bindparam(
                    "field_values",
                    value=field.get("field_values"),
                    type_=sa.dialects.postgresql.JSONB,
                ),
                sa.bindparam("field_order", value=field["field_order"]),
            )
        )

        op.execute(sa.text("""
                INSERT INTO gn_commons.cor_field_module (id_field, id_module)
                SELECT f.id_field, m.id_module
                FROM gn_commons.t_additional_fields f, gn_commons.t_modules m
                WHERE f.field_name = :field_name AND m.module_code = :module_code
            """).bindparams(field_name=field_name, module_code=field["module_code"]))

        op.execute(sa.text("""
                INSERT INTO gn_commons.cor_field_object (id_field, id_object)
                SELECT f.id_field, o.id_object
                FROM gn_commons.t_additional_fields f, gn_permissions.t_objects o
                WHERE f.field_name = :field_name AND o.code_object = :object_code
            """).bindparams(field_name=field_name, object_code=field["object_code"]))

        for shortname in FIELD_DATASETS[field_name]:
            op.execute(sa.text("""
                    INSERT INTO gn_commons.cor_field_dataset (id_field, id_dataset)
                    SELECT f.id_field, d.id_dataset
                    FROM gn_commons.t_additional_fields f, gn_meta.t_datasets d
                    WHERE f.field_name = :field_name AND d.dataset_shortname = :shortname
                """).bindparams(field_name=field_name, shortname=shortname))


def downgrade():
    # cor_field_dataset/cor_field_module/cor_field_object rows are deleted in
    # cascade with the additional fields (FKs to t_additional_fields.id_field).
    op.execute(
        sa.text(
            "DELETE FROM gn_commons.t_additional_fields WHERE field_name IN :field_names"
        ).bindparams(sa.bindparam("field_names", value=tuple(ADDITIONAL_FIELDS), expanding=True))
    )

    # OCCTAX_RELEVE/OCCTAX_OCCURRENCE support_additional_fields predates us
    # (GeoNature core default) and other data may depend on it: only revert
    # our own INDIVIDUALS object.
    op.execute(sa.text("""
        UPDATE gn_permissions.t_objects
        SET support_additional_fields = false
        WHERE code_object = 'INDIVIDUALS'
    """))

    if (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
            )
        )
        .scalar()
    ):
        # cor_module_dataset is deleted in cascade with the dataset.
        op.execute(
            sa.text("DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'")
        )

    # cor_module_dataset is deleted in cascade with each dataset.
    op.execute(
        sa.text(
            "DELETE FROM gn_meta.t_datasets WHERE dataset_shortname IN :shortnames"
        ).bindparams(sa.bindparam("shortnames", value=tuple(DATASETS), expanding=True))
    )

    op.execute(
        sa.text(
            "DELETE FROM gn_meta.t_acquisition_frameworks WHERE acquisition_framework_name = :af_name"
        ).bindparams(af_name=AF_NAME)
    )
