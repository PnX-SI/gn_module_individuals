"""Insert individuals samples data for demo

Standalone "individuals-samples" branch: not applied by `geonature db
autoupgrade`, run manually (or in CI) with:
    geonature db upgrade individuals-samples@head

Revision ID: individuals_samples
Revises:
Create Date: 2026-03-19 16:53:24.982945

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_individuals_samples"
down_revision = None
branch_labels = ("individuals-samples",)
depends_on = ("individuals",)


def upgrade():
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


def downgrade():
    conn = op.get_bind()

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
