"""Insert test data

Standalone "individuals-samples" branch: not applied by `geonature db
autoupgrade`, run manually (or in CI) with:
    geonature db upgrade individuals-samples@head

Revision ID: individuals_samples_data
Revises:
Create Date: 2026-03-19 16:53:24.982945

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "individuals_samples_data"
down_revision = None
branch_labels = ("individuals-samples",)
depends_on = ("individuals",)


def upgrade():
    conn = op.get_bind()
    op.execute(sa.text("""
            INSERT INTO gn_individual.t_tracking_devices (
    id_nomenclature_device_type,
    provider_name,
    provider_device_id,
    id_referer,
    comment,
    id_digitiser
)
SELECT
    n.id_nomenclature,
    v.provider_name,
    v.provider_device_id,
    v.id_referer,
    v.comment,
    v.id_digitiser
FROM (
    VALUES
        ('GPS', 'Ornitela', '182243', 4, 'Test balise GPS', 4),
        ('GSM', 'GSM Provider', '182A289POw', 4, 'Test balise GSM', 6),
        ('VHF', 'Lotek', '182A25POX5', 6, 'Test balise VHF/UHF', 3),
        ('VHF', 'Ornitela', '210709', 6, 'Test balise VHF', 5),
        ('GPS', 'GSM Provider', '182PO0256ARG', 3, 'Test balise GPS/GSM', 4),
        ('GSM', 'Lotek', '18256-19Z', 3, 'Test balise GSM/Lotek', 6),
        ('VHF', 'Ornitela', '210719', 4, 'Test balise VHF/Ornitela', 3),
        ('GPS', 'Lotek', '121256-AZ', 4, 'Test balise GPS/Lotek', 5),
        ('GSM', 'Ornitela', '182A87ARG', 6, 'Test balise GSM/Ornitela', 4),
        ('VHF', 'GSM Provider', '1887Y56ZA8', 3, 'Test balise VHF/GSM', 6),
        ('GPS', 'Ornitela', '182248', 4, 'Test balise GPS', 4),
        ('GSM', 'GSM Provider', '182A256POX', 4, 'Test balise GSM', 6),
        ('VHF', 'Lotek', '182A256ARG', 6, 'Test balise VHF/UHF', 3),
        ('VHF', 'Ornitela', '210710', 6, 'Test balise VHF', 5),
        ('GPS', 'GSM Provider', '182A256ATXG', 3, 'Test balise GPS/GSM', 4),
        ('GSM', 'Lotek', '18256-9G', 3, 'Test balise GSM/Lotek', 6),
        ('VHF', 'Ornitela', '210721', 4, 'Test balise VHF/Ornitela', 3),
        ('GPS', 'Lotek', '18256-9P', 4, 'Test balise GPS/Lotek', 5),
        ('GSM', 'Ornitela', '182A9P6ARP-6', 6, 'Test balise GSM/Ornitela', 4),
        ('VHF', 'GSM Provider', '182A256POM', 3, 'Test balise VHF/GSM', 6)

) AS v(mnemonique, provider_name, provider_device_id, id_referer, comment, id_digitiser)
JOIN ref_nomenclatures.t_nomenclatures n
    ON n.mnemonique = v.mnemonique;
            """))
    op.execute(sa.text("""
            INSERT INTO gn_monitoring.t_individuals
            (individual_name, cd_nom, id_nomenclature_sex, active, "comment", id_digitiser, additional_data)
            VALUES
            ('Cynthia',  459629, ref_nomenclatures.get_id_nomenclature('SEXE','2'), TRUE,  'Jolie petite femelle lagopède',  4, '{"birth_year": 2020}'),
            ('Claire',     2962, ref_nomenclatures.get_id_nomenclature('SEXE','2'), TRUE,  'Magnifique femelle tétras',      6, '{"birth_year": 2019}'),
            ('Christophe', 2962, ref_nomenclatures.get_id_nomenclature('SEXE','3'), TRUE,  'Chef de tous les tétras',        4, '{"birth_year": 2018}'),
            ('Tempête',   61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'), TRUE,  'Bouquetin marqué',               6, '{"birth_year": 2015}'),
            ('Patastrophe',61098,ref_nomenclatures.get_id_nomenclature('SEXE','3'), TRUE,  'Bouquetin marqué',               3, '{"birth_year": 2016}'),
            ('Obiwan',    61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'), TRUE,  'Bouquetin marqué',               4, '{"birth_year": 2017}'),
            ('Evasion',   61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'), TRUE,  'Bouquetin marqué',               6, '{"birth_year": 2014}'),
            ('Queen',     61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'), FALSE, 'Bouquetin marqué inactif',       3, '{"birth_year": 2013}'),
            ('Quechua',   61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'), TRUE,  'Bouquetin marqué',               3, '{"birth_year": 2012}'),
            ('Kalinka',   61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'), FALSE, 'Bouquetin marqué inactif',       4, '{"birth_year": 2011}'),
            ('Pavot',     61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'), TRUE,  'Bouquetin marqué',               4, '{"birth_year": 2019}')
            """))
    op.execute(sa.text("""
            INSERT INTO gn_individual.t_individual_deployments (
                id_individual,
                id_nomenclature_deployment_type,
                id_nomenclature_deployment_location,
                id_tracking_device,
                marking_code,
                install_date,
                removal_date,
                comment,
                id_digitiser
            )
            WITH individuals AS (
                SELECT id_individual, individual_name
                FROM gn_monitoring.t_individuals
            ),
            devices AS (
                SELECT id_tracking_device, provider_device_id
                FROM gn_individual.t_tracking_devices
            ),
            n_type AS (
                SELECT n.id_nomenclature
                FROM ref_nomenclatures.t_nomenclatures n
                JOIN ref_nomenclatures.bib_nomenclatures_types t ON t.id_type = n.id_type
                WHERE t.mnemonique = 'TYPE_MARQUAGE' AND n.mnemonique = 'DISPO_SUIVI'
            ),
            n_loc AS (
                SELECT n.id_nomenclature
                FROM ref_nomenclatures.t_nomenclatures n
                JOIN ref_nomenclatures.bib_nomenclatures_types t ON t.id_type = n.id_type
                WHERE t.mnemonique = 'LOC_MARQUAGE' AND n.mnemonique = 'ENCOLURE'
            ),
            data AS (
                SELECT *
                FROM (
                    VALUES
                    ('Cynthia', '182243', NULL, '2024-01-01', '2024-06-01', 'Premier équipement', 4),
                    ('Cynthia', '121256-AZ', NULL, '2024-06-02', NULL, 'Remplacement GPS', 4),
                    ('Claire', '182A256POX', NULL, '2025-03-15', NULL, 'Pose unique', 6),
                    ('Christophe', '210709', NULL, '2025-02-01', '2026-01-06', 'VHF actif', 4),
                    ('Christophe', '182A256ARG', NULL, '2026-01-06', NULL, 'Remplacement CHF par GPS', 4),
                    ('Tempête', '18256-9G', NULL, '2022-01-01', '2023-01-01', 'Ancien dispositif', 6),
                    ('Tempête', '210719', NULL, '2023-02-01', NULL, 'Dispositif actuel', 6),
                    ('Patastrophe', '121256-AZ', NULL, '2023-06-01', '2024-01-01', 'Retiré après suivi', 3),
                    ('Obiwan', '182A256ARG', NULL, '2024-01-10', NULL, 'Suivi GPS', 4),
                    ('Evasion', '18256-9G', NULL, '2023-03-01', '2023-09-01', 'Premier', 6),
                    ('Evasion', '182A9P6ARP-6', NULL, '2023-09-02', NULL, 'Remplacement', 6),
                    ('Queen', '1887Y56ZA8', NULL, '2022-05-01', '2023-05-01', 'Avant désactivation', 3),
                    ('Quechua', '182A256POM', NULL, '2024-02-20', NULL, 'Suivi classique', 3),
                    ('Kalinka', '210710', NULL, '2023-01-01', '2023-07-01', 'Retrait été', 4),
                    ('Pavot', '210721', NULL, '2024-03-01', NULL, 'Nouveau suivi', 4)
                ) AS t(individual_name, provider_device_id, marking_code, install_date, removal_date, comment, id_digitiser)
            )
            SELECT
                i.id_individual,
                n_type.id_nomenclature,
                n_loc.id_nomenclature,
                dev.id_tracking_device,
                d.marking_code,
                d.install_date::timestamp,
                d.removal_date::timestamp,
                d.comment,
                d.id_digitiser
            FROM data d
            JOIN individuals i ON i.individual_name = d.individual_name
            JOIN devices dev ON dev.provider_device_id = d.provider_device_id
            CROSS JOIN n_type
            CROSS JOIN n_loc
            """))

    # Physical markings: Patastrophe and Evasion (no GPS), Obiwan (with GPS).
    # Each animal: 2 colors per ear (OD, OG) + a colored collar at the neck.
    op.execute(sa.text("""
        INSERT INTO gn_individual.t_individual_deployments (
            id_individual,
            id_nomenclature_deployment_type, id_nomenclature_deployment_location,
            id_tracking_device, marking_code, install_date, id_digitiser
        )
        WITH
        individuals AS (
            SELECT id_individual, individual_name FROM gn_monitoring.t_individuals
        ),
        n_type AS (
            SELECT n.id_nomenclature, n.mnemonique
            FROM ref_nomenclatures.t_nomenclatures n
            JOIN ref_nomenclatures.bib_nomenclatures_types t ON t.id_type = n.id_type
            WHERE t.mnemonique = 'TYPE_MARQUAGE'
        ),
        n_loc AS (
            SELECT n.id_nomenclature, n.mnemonique
            FROM ref_nomenclatures.t_nomenclatures n
            JOIN ref_nomenclatures.bib_nomenclatures_types t ON t.id_type = n.id_type
            WHERE t.mnemonique = 'LOC_MARQUAGE'
        ),
        data AS (
            SELECT * FROM (VALUES
                -- Patastrophe: orange/yellow, green collar (same capture)
                ('Patastrophe', 'PLAQUE', 'OD',       'Orange', '2023-01-15', 3),
                ('Patastrophe', 'PLAQUE', 'OD',       'Jaune',  '2023-01-15', 3),
                ('Patastrophe', 'PLAQUE', 'OG',       'Orange', '2023-01-15', 3),
                ('Patastrophe', 'PLAQUE', 'OG',       'Jaune',  '2023-01-15', 3),
                ('Patastrophe', 'PLAQUE', 'ENCOLURE', 'Vert',   '2023-01-15', 3),
                -- Evasion: purple/red, yellow collar (same capture)
                ('Evasion', 'PLAQUE', 'OD',       'Violet', '2022-11-20', 6),
                ('Evasion', 'PLAQUE', 'OD',       'Rouge',  '2022-11-20', 6),
                ('Evasion', 'PLAQUE', 'OG',       'Violet', '2022-11-20', 6),
                ('Evasion', 'PLAQUE', 'OG',       'Rouge',  '2022-11-20', 6),
                ('Evasion', 'PLAQUE', 'ENCOLURE', 'Jaune',  '2022-11-20', 6),
                -- Obiwan: blue/white, red collar (same capture, same date as GPS deployment)
                ('Obiwan', 'PLAQUE', 'OD',       'Bleu',  '2024-01-10', 4),
                ('Obiwan', 'PLAQUE', 'OD',       'Blanc', '2024-01-10', 4),
                ('Obiwan', 'PLAQUE', 'OG',       'Bleu',  '2024-01-10', 4),
                ('Obiwan', 'PLAQUE', 'OG',       'Blanc', '2024-01-10', 4),
                ('Obiwan', 'PLAQUE', 'ENCOLURE', 'Rouge', '2024-01-10', 4)
            ) AS t(individual_name, type_mnemo, loc_mnemo, marking_code, install_date, id_digitiser)
        )
        SELECT
            i.id_individual,
            nt.id_nomenclature,
            nl.id_nomenclature,
            NULL,
            d.marking_code,
            d.install_date::timestamp,
            d.id_digitiser
        FROM data d
        JOIN individuals i  ON i.individual_name = d.individual_name
        JOIN n_type nt       ON nt.mnemonique     = d.type_mnemo
        JOIN n_loc nl        ON nl.mnemonique      = d.loc_mnemo;
    """))

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
                'Jeu de données de test Individus', 'INDIVIDUALS_TEST',
                'Relevés Occtax de test du module Individus',
                FALSE, TRUE, 4
            FROM gn_meta.t_acquisition_frameworks af
            WHERE af.acquisition_framework_name = 'Cadre d''acquisition de test Individus'
              AND NOT EXISTS (
                  SELECT 1 FROM gn_meta.t_datasets
                  WHERE dataset_shortname = 'INDIVIDUALS_TEST'
              )
            """))
    op.execute(sa.text("""
            INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
            SELECT m.id_module, d.id_dataset
            FROM gn_commons.t_modules m, gn_meta.t_datasets d
            WHERE m.module_code = 'OCCTAX' AND d.dataset_shortname = 'INDIVIDUALS_TEST'
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
                WHERE dataset_shortname = 'INDIVIDUALS_TEST'
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
                WHERE dataset_shortname = 'INDIVIDUALS_TEST'
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
                WHERE dataset_shortname = 'INDIVIDUALS_TEST'
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

    # --- Monitoring integration: CMR_BOUQUETIN sub-module on our marked ibex ---
    # The sub-module must have been installed beforehand via
    # ./scripts/setup_cmr_demo.sh (see that script for details).
    cmr_installed = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
        )
    ).scalar()

    if cmr_installed:
        # Dedicated dataset: the dataset "1" reused for Occtax is associated
        # (gn_commons.cor_module_dataset) with the OCCTAX module only, not CMR_BOUQUETIN.
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
                WHERE af.acquisition_framework_name = 'Cadre d''acquisition de test Individus'
                """))
        op.execute(sa.text("""
                INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
                SELECT m.id_module, d.id_dataset
                FROM gn_commons.t_modules m, gn_meta.t_datasets d
                WHERE m.module_code = 'CMR_BOUQUETIN' AND d.dataset_shortname = 'CMR_BOUQUETIN'
                """))
        op.execute(sa.text("""
                WITH site_data (base_site_name, lon, lat, id_digitiser) AS (
                    VALUES
                    ('Pointe de la Réchasse', 6.9100, 45.4050, 4),
                    ('Plan du Lac',           6.9050, 45.3160, 6),
                    ('Refuge de l''Arpont',   6.8541, 45.3350, 6),
                    ('Col d''Aussois',        6.9917, 45.2394, 3)
                )
                INSERT INTO gn_monitoring.t_base_sites (base_site_name, id_digitiser, id_inventor, geom)
                SELECT d.base_site_name, d.id_digitiser, d.id_digitiser,
                    ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326)
                FROM site_data d
                """))
        op.execute(sa.text("""
                WITH visit_data (base_site_name, visit_date, id_digitiser) AS (
                    VALUES
                    ('Pointe de la Réchasse', '2026-07-03'::date, 4),
                    ('Plan du Lac',           '2026-07-06'::date, 6),
                    ('Refuge de l''Arpont',   '2026-07-11'::date, 6),
                    ('Col d''Aussois',        '2026-07-16'::date, 3)
                ),
                cmr_module AS (
                    SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN'
                ),
                cmr_dataset AS (
                    SELECT id_dataset FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'
                )
                INSERT INTO gn_monitoring.t_base_visits (
                    id_base_site, id_dataset, id_module, id_digitiser, visit_date_min
                )
                SELECT s.id_base_site, ds.id_dataset, m.id_module, v.id_digitiser, v.visit_date
                FROM visit_data v
                JOIN gn_monitoring.t_base_sites s ON s.base_site_name = v.base_site_name
                CROSS JOIN cmr_module m
                CROSS JOIN cmr_dataset ds
                """))
        op.execute(sa.text("""
                INSERT INTO gn_monitoring.cor_visit_observer (id_base_visit, id_role)
                SELECT bv.id_base_visit, bv.id_digitiser
                FROM gn_monitoring.t_base_visits bv
                JOIN gn_monitoring.t_base_sites s ON s.id_base_site = bv.id_base_site
                WHERE s.base_site_name IN (
                    'Pointe de la Réchasse', 'Plan du Lac', 'Refuge de l''Arpont', 'Col d''Aussois'
                )
                """))
        op.execute(sa.text("""
                WITH obs_data (base_site_name, individual_name, id_digitiser) AS (
                    VALUES
                    ('Pointe de la Réchasse', 'Obiwan',     4),
                    ('Plan du Lac',           'Evasion',    6),
                    ('Refuge de l''Arpont',   'Tempête',    6),
                    ('Col d''Aussois',        'Patastrophe',3)
                )
                INSERT INTO gn_monitoring.t_observations (id_base_visit, id_digitiser, id_individual)
                SELECT bv.id_base_visit, o.id_digitiser, i.id_individual
                FROM obs_data o
                JOIN gn_monitoring.t_base_sites s ON s.base_site_name = o.base_site_name
                JOIN gn_monitoring.t_base_visits bv ON bv.id_base_site = s.id_base_site
                JOIN gn_monitoring.t_individuals i ON i.individual_name = o.individual_name
                """))


def downgrade():
    conn = op.get_bind()

    dataset = conn.execute(
        sa.text(
            "SELECT id_dataset FROM gn_meta.t_datasets WHERE dataset_shortname = 'INDIVIDUALS_TEST'"
        )
    ).scalar()

    # DELETEs on t_base_sites / t_releves_occtax cascade (ON DELETE CASCADE) to
    # visits/observations and occurrences/counts, including synthese
    # (synthese deletion triggers on occtax and monitoring).
    if conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
        )
    ).scalar():
        op.execute(sa.text("""
                DELETE FROM gn_monitoring.t_base_sites
                WHERE base_site_name IN (
                    'Pointe de la Réchasse', 'Plan du Lac', 'Refuge de l''Arpont', 'Col d''Aussois'
                )
                """))
        # cor_module_dataset is deleted in cascade with the dataset.
        op.execute(
            sa.text("DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'")
        )

    op.execute(sa.text("""
            DELETE FROM gn_monitoring.t_base_visits
            WHERE id_dataset = :dataset
            """).bindparams(dataset=dataset))

    op.execute(sa.text("""
            DELETE FROM pr_occtax.t_releves_occtax
            WHERE id_dataset = :dataset
            """).bindparams(dataset=dataset))

    # cor_module_dataset is deleted in cascade with the dataset.
    op.execute(
        sa.text("DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'INDIVIDUALS_TEST'")
    )
    op.execute(sa.text("""
            DELETE FROM gn_meta.t_acquisition_frameworks
            WHERE acquisition_framework_name = 'Cadre d''acquisition de test Individus'
            """))

    op.execute(sa.text("""
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'gn_individual' AND table_name = 't_individual_deployments') THEN
        DELETE FROM gn_individual.t_individual_deployments;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'gn_individual' AND table_name = 't_tracking_devices') THEN
        DELETE FROM gn_individual.t_tracking_devices;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema = 'gn_monitoring' AND table_name = 't_individuals') THEN
        DELETE FROM gn_monitoring.t_individuals;
    END IF;
END $$;
    """))
