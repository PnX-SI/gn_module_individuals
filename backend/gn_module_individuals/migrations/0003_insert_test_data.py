"""Insert test data

Revision ID: 0003_insert_test_data
Revises: 0002_create_tables
Create Date: 2026-03-19 16:53:24.982945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_insert_test_data'
down_revision = '0002_create_tables'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    op.execute(
        sa.text(
            """
            INSERT INTO gn_individual.bib_tracking_devices (
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
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO gn_monitoring.t_individuals
            (individual_name, cd_nom, id_nomenclature_sex, active, "comment", id_digitiser)
            VALUES
            ('Cynthia',459629, ref_nomenclatures.get_id_nomenclature('SEXE','2'),TRUE,'Jolie petite femelle lagopède',4 ),
            ('Claire',2962, ref_nomenclatures.get_id_nomenclature('SEXE','2'),TRUE,'Magnifique femelle tétras',6 ),
            ('Dominique',459629, ref_nomenclatures.get_id_nomenclature('SEXE','3'),TRUE,'Mâle lagopède acrobate',3 ),
            ('Christophe',2962, ref_nomenclatures.get_id_nomenclature('SEXE','3'),TRUE,'Chef de tous les tétras',4 ),
            ('Tempête',61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'),TRUE,'Bouquetin marqué',6 ),
            ('Patastrophe',61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'),TRUE,'Bouquetin marqué',3 ),
            ('Obiwan',61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'),TRUE,'JBouquetin marqué',4 ),
            ('Evasion',61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'),TRUE,'Bouquetin marqué',6 ),
            ('Queen',61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'),FALSE,'Bouquetin marqué inactif',3 ),
            ('Quechua',61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'),TRUE,'Bouquetin marqué',3 ),
            ('Kalinka',61098, ref_nomenclatures.get_id_nomenclature('SEXE','2'),FALSE,'Bouquetin marqué inactif',4 ),
            ('Pavot',61098, ref_nomenclatures.get_id_nomenclature('SEXE','3'),TRUE,'JBouquetin marqué',4 )
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO gn_individual.t_individual_deployments (
                id_capture,
                id_individual,
                id_nomenclature_deployment_type,
                id_nomenclature_deployment_location,
                id_tracking_device,
                marking_code,
                install_date,
                removal_date,
                comment,
                additional_data,
                id_digitiser
            )
            WITH individuals AS (
                SELECT id_individual, individual_name
                FROM gn_monitoring.t_individuals
            ),
            devices AS (
                SELECT id_tracking_device, provider_device_id
                FROM gn_individual.bib_tracking_devices
            ),
            data AS (
                SELECT *
                FROM (
                    VALUES
                    ('Cynthia', 1, '182243', 'CYN-001', '2024-01-01', '2024-06-01', 'Premier équipement','{"removal_reason": "dysfonctionnement"}'::JSON,4),
                    ('Cynthia', 2, '121256-AZ', 'CYN-002', '2024-06-02', NULL, 'Remplacement GPS','{}'::JSON, 4),
                    ('Claire', 3, '182A256POX', 'CLA-001', '2025-03-15', NULL, 'Pose unique','{}'::JSON, 6),
                    ('Dominique', 4, '182A25POX5', 'DOM-001', '2025-05-01', '2025-12-01', 'Retrait hivernal','{"removal_reason": "remplacement"}'::JSON, 3),
                    ('Christophe', 5, '210709', 'CHR-001', '2025-02-01', '2026-01-06', 'VHF actif','{"removal_reason": "matériel perdu"}'::JSON, 4),
                    ('Christophe', 6, '182A256ARG', 'CHR-002', '2026-01-06', NULL, 'Remplacement CHF par GPS','{}'::JSON, 4),
                    ('Tempête', 7, '18256-9G', 'TMP-001', '2022-01-01', '2023-01-01', 'Ancien dispositif','{"removal_reason": "dysfonctionnement"}'::JSON, 6),
                    ('Tempête', 8, '210719', 'TMP-002', '2023-02-01', NULL, 'Dispositif actuel','{}'::JSON, 6),
                    ('Patastrophe', 9, '121256-AZ', 'PAT-001', '2023-06-01', '2024-01-01', 'Retiré après suivi','{"removal_reason": "animal mort"}'::JSON, 3),
                    ('Obiwan', 10, '182A256ARG', 'OBI-001', '2024-01-10', NULL, 'Suivi GPS','{}'::JSON, 4),
                    ('Evasion', 11, '18256-9G', 'EVA-001', '2023-03-01', '2023-09-01', 'Premier','{"removal_reason": "dysfonctionnement"}'::JSON, 6),
                    ('Evasion', 12, '182A9P6ARP-6', 'EVA-002', '2023-09-02', NULL, 'Remplacement','{}'::JSON, 6),
                    ('Queen', 13, '1887Y56ZA8', 'QUE-001', '2022-05-01', '2023-05-01', 'Avant désactivation', '{"removal_reason": "remplacement"}'::JSON,3),
                    ('Quechua', 14, '182A256POM', 'QUEC-001', '2024-02-20', NULL, 'Suivi classique','{}'::JSON, 3),
                    ('Kalinka', 15, '210710', 'KAL-001', '2023-01-01', '2023-07-01', 'Retrait été','{"removal_reason": "dysfonctionnement"}'::JSON, 4),
                    ('Pavot', 16, '210721', 'PAV-001', '2024-03-01', NULL, 'Nouveau suivi','{}'::JSON, 4)
                ) AS t(individual_name, id_capture, provider_device_id, marking_code, install_date, removal_date, comment, additional_data,id_digitiser)
            )
            SELECT
                d.id_capture,
                i.id_individual,
                NULL,
                NULL,
                dev.id_tracking_device,
                d.marking_code,
                d.install_date::timestamp,
                d.removal_date::timestamp,
                d.comment,
                d.additional_data,
                d.id_digitiser
            FROM data d
            JOIN individuals i ON i.individual_name = d.individual_name
            JOIN devices dev ON dev.provider_device_id = d.provider_device_id
            """
        )
    )

def downgrade():
    conn = op.get_bind()
    op.execute(
        sa.text(
            f"""
            DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'gn_individual' 
        AND table_name = 't_individual_deployments'
    ) THEN
        DELETE FROM gn_individual.t_individual_deployments;
    END IF;

    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'gn_individual' 
        AND table_name = 'bib_tracking_devices'
    ) THEN
        DELETE FROM gn_individual.bib_tracking_devices;
    END IF;

    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'gn_monitoring' 
        AND table_name = 't_individuals'
    ) THEN
        DELETE FROM gn_monitoring.t_individuals;
    END IF;
END $$;
            """
        )
    )
