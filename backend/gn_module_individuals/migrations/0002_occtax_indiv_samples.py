"""Insert occtax individuals samples data for demo

Revision ID: 0002_occtax_indiv_samples
Revises:
Create Date: 2026-03-19 16:53:24.982945

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_occtax_indiv_samples"
down_revision = "0001_individuals_samples"


def upgrade():
    # --- Occtax integration: a few Vanoise records referencing our individuals ---
    # Dedicated acquisition framework and dataset for this test data, so no
    # hardcoded id_dataset / id_module is needed in the inserts below.
    op.execute(sa.text("""
        INSERT INTO gn_meta.t_acquisition_frameworks (
            acquisition_framework_name, acquisition_framework_desc,
            acquisition_framework_start_date
        )
        SELECT
            'Cadre d''acquisition de test Individus',
            'Cadre d''acquisition des données de test du module Individus',
            CURRENT_DATE
        WHERE NOT EXISTS (
            SELECT 1 FROM gn_meta.t_acquisition_frameworks
            WHERE acquisition_framework_name = 'Cadre d''acquisition de test Individus'
        )
    """))

    op.execute(sa.text("""
        INSERT INTO gn_meta.t_datasets (
            id_acquisition_framework, dataset_name, dataset_shortname, dataset_desc,
            marine_domain, terrestrial_domain, id_digitizer
        )
        SELECT
            af.id_acquisition_framework,
            'Jeu de données Occtax de test Individus', 'OCCTAX_INDIVIDUALS_TEST',
            'Relevés Occtax de test du module Individus',
            FALSE, TRUE, 4
        FROM gn_meta.t_acquisition_frameworks af
        WHERE af.acquisition_framework_name = 'Cadre d''acquisition de test Individus'
            AND NOT EXISTS (
                SELECT 1 FROM gn_meta.t_datasets
                WHERE dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'
            )
    """))

    op.execute(sa.text("""
        INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
        SELECT m.id_module, d.id_dataset
        FROM gn_commons.t_modules m, gn_meta.t_datasets d
        WHERE m.module_code = 'OCCTAX' AND d.dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'
    """))

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
            WHERE dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'
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
        WHERE r.place_name IN (
            'Col de la Vanoise', 'Refuge de Prariond',
            'Pointe de la Réchasse', 'Plan du Lac'
        )
    """))

    op.execute(sa.text("""
        WITH releve_species (place_name, cd_nom, nom_cite) AS (
            VALUES
            ('Col de la Vanoise',     459629, 'Lagopède alpin'),
            ('Refuge de Prariond',      2962, 'Tétras lyre'),
            ('Pointe de la Réchasse', 61098, 'Bouquetin des Alpes'),
            ('Plan du Lac',           61098, 'Bouquetin des Alpes')
        )
        INSERT INTO pr_occtax.t_occurrences_occtax (
            id_releve_occtax, cd_nom, nom_cite, meta_v_taxref
        )
        SELECT r.id_releve_occtax, s.cd_nom, s.nom_cite, 'Taxref v18'
        FROM pr_occtax.t_releves_occtax r
        JOIN releve_species s ON s.place_name = r.place_name
        WHERE r.place_name IN (
            'Col de la Vanoise', 'Refuge de Prariond',
            'Pointe de la Réchasse', 'Plan du Lac'
        )
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
        JOIN occ_individual oi ON oi.place_name = r.place_name
        JOIN gn_monitoring.t_individuals i ON i.individual_name = oi.individual_name
        WHERE r.place_name IN (
            'Col de la Vanoise', 'Refuge de Prariond',
            'Pointe de la Réchasse', 'Plan du Lac'
        )
    """))

    # Field sightings identified by physical marking (no place name, random
    # positions in Vanoise): Patastrophe (5), Evasion (3), Obiwan (0), covering
    # the requested 0-5 range so movement can be tested.
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
            WHERE dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'
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
        INSERT INTO pr_occtax.t_occurrences_occtax (id_releve_occtax, cd_nom, nom_cite, meta_v_taxref)
        SELECT r.id_releve_occtax, 61098, 'Bouquetin des Alpes', 'Taxref v18'
        FROM pr_occtax.t_releves_occtax r
        WHERE r.date_min IN (
            '2026-07-01 10:15', '2026-07-04 14:40', '2026-07-08 09:05',
            '2026-07-12 16:20', '2026-07-15 08:50',
            '2026-07-03 11:30', '2026-07-10 13:10', '2026-07-18 07:55'
        )
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
            WHERE dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'
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


def downgrade():
    conn = op.get_bind()

    dataset = conn.execute(
        sa.text(
            "SELECT id_dataset FROM gn_meta.t_datasets WHERE dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'"
        )
    ).scalar()

    # DELETEs (ON DELETE CASCADE) to
    # visits/observations and occurrences/counts, including synthese
    # (synthese deletion triggers on occtax and monitoring).
    op.execute(sa.text("""
        DELETE FROM pr_occtax.t_releves_occtax
        WHERE id_dataset = :dataset
        """).bindparams(dataset=dataset))

    # cor_module_dataset is deleted in cascade with the dataset.
    op.execute(
        sa.text(
            "DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'OCCTAX_INDIVIDUALS_TEST'"
        )
    )

    op.execute(sa.text("""
        DELETE FROM gn_meta.t_acquisition_frameworks
        WHERE acquisition_framework_name = 'Cadre d''acquisition de test Individus'
    """))
