"""Insert Occtax observation and captures

Individuals-samples demo data.

Observations (marked bouquetins, tracking) and captures
(bouquetins and tétras-lyre), with the additional
fields from smpl0001_metadata, and link individuals to modules (OCCTAX, and
CMR_BOUQUETIN if installed) via cor_individual_module.

Revision ID: smpl0003_captures_occtax
Revises: smpl0002_devices_individuals
Create Date: 2026-09-18 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "smpl0003_captures_occtax"
down_revision = "smpl0002_devices_individuals"


def upgrade():
    conn = op.get_bind()

    # --- Occtax sightings: a few Vanoise records referencing our individuals,
    # in the "Occtax bouquetins marqués" dataset (created by smpl0001) ---
    op.execute(sa.text("""
        WITH releve_data (place_name, lon, lat, obs_date, id_digitiser) AS (
            VALUES
            ('Col de la Vanoise',    6.9313, 45.3944, '2026-07-02 09:30'::timestamp, 4),
            ('Refuge de Prariond',   6.9800, 45.4500, '2026-07-05 07:15'::timestamp, 6),
            ('Pointe de la Réchasse',6.9100, 45.4050, '2026-07-09 11:00'::timestamp, 4),
            ('Plan du Lac',          6.9050, 45.3160, '2026-07-14 08:45'::timestamp, 6)
        ),
        occtax_module AS (
            SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'OCCTAX'
        ),
        test_dataset AS (
            SELECT id_dataset FROM gn_meta.t_datasets
            WHERE dataset_shortname = 'OCCTAX_BOUQMARQ_TEST'
        )
        INSERT INTO pr_occtax.t_releves_occtax (
            id_dataset, id_digitiser, id_module, date_min, date_max,
            place_name, geom_4326, geom_local
        )
        SELECT
            ds.id_dataset,
            d.id_digitiser,
            m.id_module,
            d.obs_date,
            d.obs_date,
            d.place_name,
            ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326),
            ST_Transform(ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326), 2154)
        FROM releve_data d
        CROSS JOIN occtax_module m
        CROSS JOIN test_dataset ds
    """))

    # Col de la Vanoise: 2 observers, Refuge de Prariond: 3 observers,
    # the other two keep a single observer (their own id_digitiser) to
    # cover the 1/2/3-observer display cases.
    op.execute(sa.text("""
        WITH observer_data (place_name, id_role) AS (
            VALUES
            ('Col de la Vanoise', 4),
            ('Col de la Vanoise', 6),
            ('Refuge de Prariond', 6),
            ('Refuge de Prariond', 3),
            ('Refuge de Prariond', 4),
            ('Pointe de la Réchasse', 4),
            ('Plan du Lac', 6)
        )
        INSERT INTO pr_occtax.cor_role_releves_occtax (id_releve_occtax, id_role)
        SELECT r.id_releve_occtax, o.id_role
        FROM pr_occtax.t_releves_occtax r
        JOIN observer_data o ON o.place_name = r.place_name
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        WHERE ds.dataset_shortname = 'OCCTAX_BOUQMARQ_TEST'
    """))

    # Plan du Lac is Evasion's sighting (bouquetin femelle) : with_young is set.
    op.execute(sa.text("""
        WITH releve_species (place_name, cd_nom, nom_cite, with_young) AS (
            VALUES
            ('Col de la Vanoise',     459629, 'Lagopède alpin',      NULL),
            ('Refuge de Prariond',      2962, 'Tétras lyre',         NULL),
            ('Pointe de la Réchasse', 61098, 'Bouquetin des Alpes',  NULL),
            ('Plan du Lac',           61098, 'Bouquetin des Alpes',  'Probable')
        )
        INSERT INTO pr_occtax.t_occurrences_occtax (
            id_releve_occtax, cd_nom, nom_cite, meta_v_taxref, additional_fields
        )
        SELECT
            r.id_releve_occtax, s.cd_nom, s.nom_cite, 'Taxref v18',
            CASE WHEN s.with_young IS NOT NULL
                THEN jsonb_build_object('with_young', s.with_young)
            END
        FROM pr_occtax.t_releves_occtax r
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        JOIN releve_species s ON s.place_name = r.place_name
        WHERE ds.dataset_shortname = 'OCCTAX_BOUQMARQ_TEST'
    """))

    op.execute(sa.text("""
        WITH occ_individual (place_name, individual_name) AS (
            VALUES
            ('Col de la Vanoise', 'Cynthia'),
            ('Refuge de Prariond', 'Claire'),
            ('Pointe de la Réchasse', 'Obiwan'),
            ('Plan du Lac', 'Evasion')
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
        WHERE ds.dataset_shortname = 'OCCTAX_BOUQMARQ_TEST'
    """))

    # Field sightings identified by physical marking (no place name, random
    # positions in Vanoise): Patastrophe (5, male), Evasion (3, female,
    # with_young set), Obiwan (0), covering the requested 0-5 range so
    # movement can be tested.
    op.execute(sa.text("""
        WITH sighting_data (individual_name, lon, lat, obs_date, id_digitiser) AS (
            VALUES
            ('Patastrophe', 6.72, 45.25, '2026-07-01 10:15'::timestamp, 3),
            ('Patastrophe', 6.88, 45.47, '2026-07-04 14:40'::timestamp, 3),
            ('Patastrophe', 6.95, 45.33, '2026-07-08 09:05'::timestamp, 3),
            ('Patastrophe', 6.70, 45.41, '2026-07-12 16:20'::timestamp, 3),
            ('Patastrophe', 7.01, 45.29, '2026-07-15 08:50'::timestamp, 3),
            ('Evasion',     6.80, 45.38, '2026-07-03 11:30'::timestamp, 6),
            ('Evasion',     6.93, 45.45, '2026-07-10 13:10'::timestamp, 6),
            ('Evasion',     6.75, 45.22, '2026-07-18 07:55'::timestamp, 6)
        ),
        occtax_module AS (
            SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'OCCTAX'
        ),
        test_dataset AS (
            SELECT id_dataset FROM gn_meta.t_datasets
            WHERE dataset_shortname = 'OCCTAX_BOUQMARQ_TEST'
        )
        INSERT INTO pr_occtax.t_releves_occtax (
            id_dataset, id_digitiser, id_module, date_min, date_max, geom_4326, geom_local
        )
        SELECT
            ds.id_dataset, d.id_digitiser, m.id_module, d.obs_date, d.obs_date,
            ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326),
            ST_Transform(ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326), 2154)
        FROM sighting_data d
        CROSS JOIN occtax_module m
        CROSS JOIN test_dataset ds
    """))

    op.execute(sa.text("""
        INSERT INTO pr_occtax.cor_role_releves_occtax (id_releve_occtax, id_role)
        SELECT DISTINCT r.id_releve_occtax, CASE WHEN r.date_min < '2026-07-06' THEN 3 ELSE 6 END
        FROM pr_occtax.t_releves_occtax r
        WHERE r.date_min IN (
            '2026-07-01 10:15', '2026-07-04 14:40', '2026-07-08 09:05',
            '2026-07-12 16:20', '2026-07-15 08:50',
            '2026-07-03 11:30', '2026-07-10 13:10', '2026-07-18 07:55'
        )
        """))

    op.execute(sa.text("""
        WITH sighting_individual (obs_date, individual_name, with_young) AS (
            VALUES
            ('2026-07-01 10:15'::timestamp, 'Patastrophe', NULL),
            ('2026-07-04 14:40'::timestamp, 'Patastrophe', NULL),
            ('2026-07-08 09:05'::timestamp, 'Patastrophe', NULL),
            ('2026-07-12 16:20'::timestamp, 'Patastrophe', NULL),
            ('2026-07-15 08:50'::timestamp, 'Patastrophe', NULL),
            ('2026-07-03 11:30'::timestamp, 'Evasion',     'Certain'),
            ('2026-07-10 13:10'::timestamp, 'Evasion',     'Certain'),
            ('2026-07-18 07:55'::timestamp, 'Evasion',     'Absence')
        )
        INSERT INTO pr_occtax.t_occurrences_occtax (id_releve_occtax, cd_nom, nom_cite, meta_v_taxref, additional_fields)
        SELECT
            r.id_releve_occtax, 61098, 'Bouquetin des Alpes', 'Taxref v18',
            CASE WHEN si.with_young IS NOT NULL
                THEN jsonb_build_object('with_young', si.with_young)
            END
        FROM pr_occtax.t_releves_occtax r
        JOIN sighting_individual si ON si.obs_date = r.date_min
        """))

    op.execute(sa.text("""
        WITH sighting_individual (obs_date, individual_name) AS (
            VALUES
            ('2026-07-01 10:15'::timestamp, 'Patastrophe'),
            ('2026-07-04 14:40'::timestamp, 'Patastrophe'),
            ('2026-07-08 09:05'::timestamp, 'Patastrophe'),
            ('2026-07-12 16:20'::timestamp, 'Patastrophe'),
            ('2026-07-15 08:50'::timestamp, 'Patastrophe'),
            ('2026-07-03 11:30'::timestamp, 'Evasion'),
            ('2026-07-10 13:10'::timestamp, 'Evasion'),
            ('2026-07-18 07:55'::timestamp, 'Evasion')
        )
        INSERT INTO pr_occtax.cor_counting_occtax (
            id_occurrence_occtax, count_min, count_max, id_individual
        )
        SELECT o.id_occurrence_occtax, 1, 1, i.id_individual
        FROM pr_occtax.t_occurrences_occtax o
        JOIN pr_occtax.t_releves_occtax r ON r.id_releve_occtax = o.id_releve_occtax
        JOIN sighting_individual si ON si.obs_date = r.date_min
        JOIN gn_monitoring.t_individuals i ON i.individual_name = si.individual_name
        """))

    # Simulated GPS tag data: 4 points/day over 3 days, 100m apart,
    # for a single animal (Cynthia).
    op.execute(sa.text("""
        WITH RECURSIVE gps_points(seq, geom) AS (
            SELECT 1, ST_SetSRID(ST_MakePoint(6.9200, 45.4100), 4326)
            UNION ALL
            SELECT seq + 1,
                ST_Project(geom::geography, 100, radians((seq * 35)::float))::geometry
            FROM gps_points
            WHERE seq < 12
        ),
        gps_times (seq, fix_time) AS (
            VALUES
            (1, '2026-07-20 06:00'::timestamp), (2, '2026-07-20 12:00'::timestamp),
            (3, '2026-07-20 18:00'::timestamp), (4, '2026-07-20 22:00'::timestamp),
            (5, '2026-07-21 06:00'::timestamp), (6, '2026-07-21 12:00'::timestamp),
            (7, '2026-07-21 18:00'::timestamp), (8, '2026-07-21 22:00'::timestamp),
            (9, '2026-07-22 06:00'::timestamp), (10, '2026-07-22 12:00'::timestamp),
            (11, '2026-07-22 18:00'::timestamp), (12, '2026-07-22 22:00'::timestamp)
        ),
        occtax_module AS (
            SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'OCCTAX'
        ),
        test_dataset AS (
            SELECT id_dataset FROM gn_meta.t_datasets
            WHERE dataset_shortname = 'OCCTAX_BOUQMARQ_TEST'
        )
        INSERT INTO pr_occtax.t_releves_occtax (
            id_dataset, id_digitiser, id_module, date_min, date_max, geom_4326, geom_local
        )
        SELECT ds.id_dataset, 4, m.id_module, t.fix_time, t.fix_time, p.geom, ST_Transform(p.geom, 2154)
        FROM gps_points p
        JOIN gps_times t ON t.seq = p.seq
        CROSS JOIN occtax_module m
        CROSS JOIN test_dataset ds
    """))

    op.execute(sa.text("""
        INSERT INTO pr_occtax.cor_role_releves_occtax (id_releve_occtax, id_role)
        SELECT r.id_releve_occtax, 4
        FROM pr_occtax.t_releves_occtax r
        WHERE r.date_min BETWEEN '2026-07-20 00:00' AND '2026-07-22 23:59'
    """))

    op.execute(sa.text("""
        INSERT INTO pr_occtax.t_occurrences_occtax (id_releve_occtax, cd_nom, nom_cite, meta_v_taxref)
        SELECT r.id_releve_occtax, 459629, 'Lagopède alpin', 'Taxref v18'
        FROM pr_occtax.t_releves_occtax r
        WHERE r.date_min BETWEEN '2026-07-20 00:00' AND '2026-07-22 23:59'
    """))

    op.execute(sa.text("""
        INSERT INTO pr_occtax.cor_counting_occtax (
            id_occurrence_occtax, count_min, count_max, id_individual
        )
        SELECT o.id_occurrence_occtax, 1, 1, i.id_individual
        FROM pr_occtax.t_occurrences_occtax o
        JOIN pr_occtax.t_releves_occtax r ON r.id_releve_occtax = o.id_releve_occtax
        JOIN gn_monitoring.t_individuals i ON i.individual_name = 'Cynthia'
        WHERE r.date_min BETWEEN '2026-07-20 00:00' AND '2026-07-22 23:59'
    """))

    # --- Bouquetin captures: dates match the tracking device/marking
    # install_date from smpl0002 (the capture is when it was fitted) ---
    op.execute(sa.text("""
        WITH capture_data (
            place_name, lon, lat, capture_date, id_digitiser, capture_type, capture_event
        ) AS (
            VALUES
            ('Refuge de l''Arpont',       6.8541, 45.3350, '2022-05-01 08:00'::timestamp, 3, 'Téléanesthésie', 'Capture'),
            ('Col d''Aussois',            6.9917, 45.2394, '2023-01-01 07:30'::timestamp, 4, 'Filet',          'Capture'),
            ('Fond d''Aussois',           6.9700, 45.2200, '2024-02-20 09:00'::timestamp, 3, 'Cage',           'Capture'),
            ('Refuge du Fond d''Aussois', 6.9650, 45.2450, '2024-03-01 08:15'::timestamp, 4, 'Téléanesthésie', 'Capture')
        ),
        occtax_module AS (
            SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'OCCTAX'
        ),
        capture_dataset AS (
            SELECT id_dataset FROM gn_meta.t_datasets
            WHERE dataset_shortname = 'CAPTURES_BOUQUETIN_TEST'
        )
        INSERT INTO pr_occtax.t_releves_occtax (
            id_dataset, id_digitiser, id_module, date_min, date_max,
            place_name, grp_method, comment, geom_4326, geom_local, additional_fields
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
            ST_Transform(ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326), 2154),
            jsonb_build_object('capture_type', d.capture_type, 'capture_event', d.capture_event)
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
        WHERE ds.dataset_shortname = 'CAPTURES_BOUQUETIN_TEST'
    """))

    op.execute(sa.text("""
        WITH occ_data (place_name, weight, horn_size) AS (
            VALUES
            ('Refuge de l''Arpont',           38.0, 12),
            ('Col d''Aussois',                45.5, 18),
            ('Fond d''Aussois',                65.0, 62),
            ('Refuge du Fond d''Aussois',      68.5, 65)
        )
        INSERT INTO pr_occtax.t_occurrences_occtax (
            id_releve_occtax, cd_nom, nom_cite, meta_v_taxref, additional_fields
        )
        SELECT
            r.id_releve_occtax, 61098, 'Bouquetin des Alpes', 'Taxref v18',
            jsonb_build_object('weight', o.weight, 'horn_size', o.horn_size)
        FROM pr_occtax.t_releves_occtax r
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        JOIN occ_data o ON o.place_name = r.place_name
        WHERE ds.dataset_shortname = 'CAPTURES_BOUQUETIN_TEST'
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
        WHERE ds.dataset_shortname = 'CAPTURES_BOUQUETIN_TEST'
    """))

    # --- Tétras-lyre captures: Christophe's capture matches his 2026-01-06
    # device replacement (recapture), Claire's matches her single device
    # install (capture) ---
    op.execute(sa.text("""
        WITH capture_data (
            place_name, lon, lat, capture_date, id_digitiser, capture_type, capture_event, individual_name
        ) AS (
            VALUES
            ('Refuge du Fond des Fours', 6.8233, 45.3667, '2025-03-15 09:00'::timestamp, 6, 'Filet', 'Capture',   'Claire'),
            ('Col de la Leisse',         6.9847, 45.4144, '2026-01-06 08:30'::timestamp, 4, 'Cage',  'Recapture', 'Christophe')
        ),
        occtax_module AS (
            SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'OCCTAX'
        ),
        capture_dataset AS (
            SELECT id_dataset FROM gn_meta.t_datasets
            WHERE dataset_shortname = 'CAPTURES_TETRAS_TEST'
        )
        INSERT INTO pr_occtax.t_releves_occtax (
            id_dataset, id_digitiser, id_module, date_min, date_max,
            place_name, grp_method, comment, geom_4326, geom_local, additional_fields
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
            ST_Transform(ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326), 2154),
            jsonb_build_object('capture_type', d.capture_type, 'capture_event', d.capture_event)
        FROM capture_data d
        CROSS JOIN occtax_module m
        CROSS JOIN capture_dataset ds
    """))

    op.execute(sa.text("""
        WITH observer_data (place_name, id_role) AS (
            VALUES
            ('Refuge du Fond des Fours', 6),
            ('Refuge du Fond des Fours', 4),
            ('Col de la Leisse', 4)
        )
        INSERT INTO pr_occtax.cor_role_releves_occtax (id_releve_occtax, id_role)
        SELECT r.id_releve_occtax, o.id_role
        FROM pr_occtax.t_releves_occtax r
        JOIN observer_data o ON o.place_name = r.place_name
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        WHERE ds.dataset_shortname = 'CAPTURES_TETRAS_TEST'
    """))

    op.execute(sa.text("""
        WITH occ_data (place_name, weight, wing_size) AS (
            VALUES
            ('Refuge du Fond des Fours', 1.05, 27),
            ('Col de la Leisse',         1.35, 31)
        )
        INSERT INTO pr_occtax.t_occurrences_occtax (
            id_releve_occtax, cd_nom, nom_cite, meta_v_taxref, additional_fields
        )
        SELECT
            r.id_releve_occtax, 2962, 'Tétras lyre', 'Taxref v18',
            jsonb_build_object('weight', o.weight, 'wing_size', o.wing_size)
        FROM pr_occtax.t_releves_occtax r
        JOIN gn_meta.t_datasets ds ON ds.id_dataset = r.id_dataset
        JOIN occ_data o ON o.place_name = r.place_name
        WHERE ds.dataset_shortname = 'CAPTURES_TETRAS_TEST'
    """))

    op.execute(sa.text("""
        WITH occ_individual (place_name, individual_name) AS (
            VALUES
            ('Refuge du Fond des Fours', 'Claire'),
            ('Col de la Leisse', 'Christophe')
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
        WHERE ds.dataset_shortname = 'CAPTURES_TETRAS_TEST'
    """))

    # --- Link individuals to modules (gn_monitoring.cor_individual_module) ---

    # OCCTAX: every individual that already has an Occtax occurrence
    # (sightings, GPS track, or captures inserted above), plus every
    # bouquetin (cd_nom 61098) regardless of whether it has an occurrence, so
    # the whole CMR_BOUQUETIN population is consistently attached to OCCTAX too.
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
    # smpl0001/smpl0004. Every bouquetin (cd_nom 61098), regardless of
    # whether it has a sample observation in that sub-module.
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
    op.execute(sa.text("""
        DELETE FROM pr_occtax.t_releves_occtax r
        USING gn_meta.t_datasets ds
        WHERE r.id_dataset = ds.id_dataset
          AND ds.dataset_shortname IN (
              'OCCTAX_BOUQMARQ_TEST', 'CAPTURES_BOUQUETIN_TEST', 'CAPTURES_TETRAS_TEST'
          )
        """))

    op.execute(sa.text("""
        DELETE FROM gn_monitoring.cor_individual_module cim
        USING gn_commons.t_modules m
        WHERE cim.id_module = m.id_module AND m.module_code IN ('OCCTAX', 'CMR_BOUQUETIN')
    """))
