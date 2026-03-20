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
            f"""
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
        ('GSM', 'GSM Provider', '182A256POX', 4, 'Test balise GSM', 6),
        ('VHF', 'Lotek', '182A25POX5', 6, 'Test balise VHF/UHF', 3),
        ('VHF', 'Ornitela', '210709', 6, 'Test balise VHF', 5),
        ('GPS', 'GSM Provider', '182A256ARG', 3, 'Test balise GPS/GSM', 4),
        ('GSM', 'Lotek', '18256-9G', 3, 'Test balise GSM/Lotek', 6),
        ('VHF', 'Ornitela', '210719', 4, 'Test balise VHF/Ornitela', 3),
        ('GPS', 'Lotek', '121256-AZ', 4, 'Test balise GPS/Lotek', 5),
        ('GSM', 'Ornitela', '182A256ARG', 6, 'Test balise GSM/Ornitela', 4),
        ('VHF', 'GSM Provider', '1887Y56ZA8', 3, 'Test balise VHF/GSM', 6),
        ('GPS', 'Ornitela', '182243', 4, 'Test balise GPS', 4),
        ('GSM', 'GSM Provider', '182A256POX', 4, 'Test balise GSM', 6),
        ('VHF', 'Lotek', '182A256ARG', 6, 'Test balise VHF/UHF', 3),
        ('VHF', 'Ornitela', '210710', 6, 'Test balise VHF', 5),
        ('GPS', 'GSM Provider', '182A256ATXG', 3, 'Test balise GPS/GSM', 4),
        ('GSM', 'Lotek', '18256-9G', 3, 'Test balise GSM/Lotek', 6),
        ('VHF', 'Ornitela', '210721', 4, 'Test balise VHF/Ornitela', 3),
        ('GPS', 'Lotek', '18256-9G', 4, 'Test balise GPS/Lotek', 5),
        ('GSM', 'Ornitela', '182A9P6ARP-6', 6, 'Test balise GSM/Ornitela', 4),
        ('VHF', 'GSM Provider', '182A256POM', 3, 'Test balise VHF/GSM', 6)
        
) AS v(mnemonique, provider_name, provider_device_id, id_referer, comment, id_digitiser)
JOIN ref_nomenclatures.t_nomenclatures n
    ON n.mnemonique = v.mnemonique;
            """
        )
    )


def downgrade():
    conn = op.get_bind()
    op.execute(
        sa.text(
            f"""
            DELETE FROM gn_individual.bib_tracking_devices;
            """
        )
    )
