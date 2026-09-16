"""Insert Occtax capture samples data for demo, and link individuals to
modules (OCCTAX, and CMR_BOUQUETIN if installed) via cor_individual_module.

Revision ID: 0005_occtax_captures_samples
Revises: 0004_additional_fields_samples
Create Date: 2026-09-16 11:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_occtax_captures_samples"
down_revision = "0004_additional_fields_samples"


def upgrade():
    conn = op.get_bind()

    # --- Dedicated dataset for capture events, distinct from the sightings/
    # tracking dataset created by 0002_occtax_indiv_samples (OCCTAX_INDIVIDUALS_TEST) ---
    op.execute(sa.text("""
        INSERT INTO gn_meta.t_datasets (
            id_acquisition_framework, dataset_name, dataset_shortname, dataset_desc,
            marine_domain, terrestrial_domain, id_digitizer
        )
        SELECT
            af.id_acquisition_framework,
            'Jeu de données Occtax captures TEST', 'OCCTAX_CAPTURES_TEST',
            'Captures physiques (pose de marquage, mesures biométriques) saisies dans Occtax',
            FALSE, TRUE, 4
        FROM gn_meta.t_acquisition_frameworks af
        WHERE af.acquisition_framework_name = 'Cadre d''acquisition de test Individus'
            AND NOT EXISTS (
                SELECT 1 FROM gn_meta.t_datasets
                WHERE dataset_shortname = 'OCCTAX_CAPTURES_TEST'
            )
    """))

    op.execute(sa.text("""
        INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
        SELECT m.id_module, d.id_dataset
        FROM gn_commons.t_modules m, gn_meta.t_datasets d
        WHERE m.module_code = 'OCCTAX' AND d.dataset_shortname = 'OCCTAX_CAPTURES_TEST'
    """))

    # Capture dates match the tracking device install_date from
    # 0001_individuals_samples: the capture is when the device/marking was fitted.
    op.execute(sa.text("""
        WITH capture_data (place_name, lon, lat, capture_date, id_digitiser) AS (
            VALUES
            ('Refuge de l''Arpont',    6.8541, 45.3350, '2022-05-01 08:00'::timestamp, 3),
            ('Col d''Aussois',         6.9917, 45.2394, '2023-01-01 07:30'::timestamp, 4),
            ('Fond d''Aussois',        6.9700, 45.2200, '2024-02-20 09:00'::timestamp, 3),
            ('Refuge du Fond d''Aussois', 6.9650, 45.2450, '2024-03-01 08:15'::timestamp, 4)
        ),
        occtax_module AS (
            SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'OCCTAX'
        ),
        capture_dataset AS (
            SELECT id_dataset FROM gn_meta.t_datasets
            WHERE dataset_shortname = 'OCCTAX_CAPTURES_TEST'
        )
        INSERT INTO pr_occtax.t_releves_occtax (
            id_dataset, id_digitiser, id_module, date_min, date_max,
            place_name, grp_method, comment, geom_4326, geom_local
        )
        SELECT
            ds.id_dataset,
            d.id_digitiser,
            m.id_module,
            d.capture_date,
            d.capture_date,
            d.place_name,
            'Capture',
            'Capture physique : pose de marquage et mesures biométriques',
            ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326),
            ST_Transform(ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326), 2154)
        FROM capture_data d
        CROSS JOIN occtax_module m
        CROSS JOIN capture_dataset ds
    """))

    op.execute(sa.text("""
        WITH observer_data (place_name, id_role) AS (
            VALUES
            ('Refuge de l''Arpont', 3),
            ('Refuge de l''Arpont', 6),
            ('Col d''Aussois', 4),
            ('Fond d''Aussois', 3),
            ('Fond d''Aussois', 6),
            ('Refuge du Fond d''Aussois', 4)
        )
        INSERT INTO pr_occtax.cor_role_releves_occtax (id_releve_occtax, id_role)
        SELECT r.id_releve_occtax, o.id_role
        FROM pr_occtax.t_releves_occtax r
        JOIN observer_data o ON o.place_name = r.place_name
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        WHERE ds.dataset_shortname = 'OCCTAX_CAPTURES_TEST'
    """))

    op.execute(sa.text("""
        WITH occ_data (place_name, weight_kg, chest_girth_cm, horn_length_cm, body_condition) AS (
            VALUES
            ('Refuge de l''Arpont',           38.0, 78,  12, 'Bon état général, légèrement amaigrie'),
            ('Col d''Aussois',                45.5, 92,  18, 'Bon état général'),
            ('Fond d''Aussois',                65.0, 105, 62, 'Excellent état, cornes bien développées'),
            ('Refuge du Fond d''Aussois',      68.5, 108, 65, 'Excellent état, individu dominant')
        )
        INSERT INTO pr_occtax.t_occurrences_occtax (
            id_releve_occtax, cd_nom, nom_cite, meta_v_taxref, comment, additional_fields
        )
        SELECT
            r.id_releve_occtax, 61098, 'Bouquetin des Alpes', 'Taxref v18',
            'Mesures prises lors de la capture',
            jsonb_build_object(
                'weight_kg', o.weight_kg,
                'chest_girth_cm', o.chest_girth_cm,
                'horn_length_cm', o.horn_length_cm,
                'body_condition', o.body_condition
            )
        FROM pr_occtax.t_releves_occtax r
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        JOIN occ_data o ON o.place_name = r.place_name
        WHERE ds.dataset_shortname = 'OCCTAX_CAPTURES_TEST'
    """))

    op.execute(sa.text("""
        WITH occ_individual (place_name, individual_name) AS (
            VALUES
            ('Refuge de l''Arpont', 'Queen'),
            ('Col d''Aussois', 'Kalinka'),
            ('Fond d''Aussois', 'Quechua'),
            ('Refuge du Fond d''Aussois', 'Pavot')
        )
        INSERT INTO pr_occtax.cor_counting_occtax (
            id_occurrence_occtax, count_min, count_max, id_individual
        )
        SELECT o.id_occurrence_occtax, 1, 1, i.id_individual
        FROM pr_occtax.t_occurrences_occtax o
        JOIN pr_occtax.t_releves_occtax r ON r.id_releve_occtax = o.id_releve_occtax
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        JOIN occ_individual oi ON oi.place_name = r.place_name
        JOIN gn_monitoring.t_individuals i ON i.individual_name = oi.individual_name
        WHERE ds.dataset_shortname = 'OCCTAX_CAPTURES_TEST'
    """))

    # --- Link individuals to modules (gn_monitoring.cor_individual_module) ---

    # OCCTAX: every individual that already has an Occtax occurrence (sightings
    # from 0002_occtax_indiv_samples, GPS track, or the captures just inserted
    # above), plus every bouquetin (cd_nom 61098) regardless of whether it has
    # an occurrence, so the whole CMR_BOUQUETIN population is consistently
    # attached to OCCTAX too.
    op.execute(sa.text("""
        INSERT INTO gn_monitoring.cor_individual_module (id_individual, id_module)
        SELECT DISTINCT i.id_individual, m.id_module
        FROM gn_monitoring.t_individuals i
        CROSS JOIN gn_commons.t_modules m
        WHERE m.module_code = 'OCCTAX'
          AND (
            i.cd_nom = 61098
            OR EXISTS (
                SELECT 1 FROM pr_occtax.cor_counting_occtax cc
                WHERE cc.id_individual = i.id_individual
            )
          )
        ON CONFLICT DO NOTHING
    """))

    # CMR_BOUQUETIN (monitoring sub-module): only if installed, same guard as
    # 0003_monitoring_indiv_samples. Every bouquetin (cd_nom 61098), regardless
    # of whether it has a sample observation in that sub-module.
    cmr_installed = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
        )
    ).scalar()

    if cmr_installed:
        op.execute(sa.text("""
            INSERT INTO gn_monitoring.cor_individual_module (id_individual, id_module)
            SELECT DISTINCT i.id_individual, m.id_module
            FROM gn_monitoring.t_individuals i
            CROSS JOIN gn_commons.t_modules m
            WHERE m.module_code = 'CMR_BOUQUETIN' AND i.cd_nom = 61098
            ON CONFLICT DO NOTHING
        """))


def downgrade():
    conn = op.get_bind()

    dataset = conn.execute(
        sa.text(
            "SELECT id_dataset FROM gn_meta.t_datasets WHERE dataset_shortname = 'OCCTAX_CAPTURES_TEST'"
        )
    ).scalar()

    op.execute(sa.text("""
        DELETE FROM pr_occtax.t_releves_occtax
        WHERE id_dataset = :dataset
        """).bindparams(dataset=dataset))

    # cor_module_dataset is deleted in cascade with the dataset.
    op.execute(
        sa.text("DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'OCCTAX_CAPTURES_TEST'")
    )

    op.execute(sa.text("""
        DELETE FROM gn_monitoring.cor_individual_module cim
        USING gn_commons.t_modules m
        WHERE cim.id_module = m.id_module AND m.module_code IN ('OCCTAX', 'CMR_BOUQUETIN')
    """))
