"""Create tables

Revision ID: 0002_create_tables
Revises: 0001_init_migrations
Create Date: 2026-03-19 15:40:48.398854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_create_tables'
down_revision = '0001_init_migrations'
branch_labels = None
depends_on = None

MODULE_CODE = "INDIVIDUALS"
SCHEMA_NAME = "gn_individual"

def upgrade():
    conn = op.get_bind()
    bib_tracking_devices = op.create_table(
        "bib_tracking_devices",
        sa.Column(
            "id_tracking_device",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "id_nomenclature_device_type",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "provider_name",
            sa.Text(),
            nullable=True,
        ),
      sa.Column(
            "provider_device_id",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id_referer",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.t_roles.id_role"),
            nullable=True,
        ),
        sa.Column(
            "comment",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id_digitiser",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.t_roles.id_role"),
            nullable=True,
        ),
        sa.Column(
            "meta_create_date",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "meta_update_date",
            sa.DateTime(),
            nullable=True,
        ),
        schema=SCHEMA_NAME,
    )
    op.execute(f"""
        CREATE OR REPLACE FUNCTION {SCHEMA_NAME}.set_meta_dates()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                NEW.meta_create_date := NOW();
                NEW.meta_update_date := NOW();
            ELSIF TG_OP = 'UPDATE' THEN
                NEW.meta_update_date := NOW();
                NEW.meta_create_date := OLD.meta_create_date;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute(f"""
        CREATE TRIGGER tr_meta_dates_bib_tracking_devices
        BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.bib_tracking_devices
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA_NAME}.set_meta_dates();
    """)

    op.execute(
        sa.text(
            f"""
            INSERT INTO ref_nomenclatures.bib_nomenclatures_types (id_type,mnemonique,label_default,definition_default,label_fr,definition_fr,source) 
            VALUES (129,'TYPE_CAPTEUR', 'Type de capteur de position', 'Capteur de position','Type de capteur de position', 'Capteur de position', 'GEONATURE')  
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            INSERT INTO ref_nomenclatures.t_nomenclatures (id_type,	cd_nomenclature,mnemonique,label_default,definition_default,label_fr,definition_fr,
            source,	hierarchy,active)
            VALUES (129,1,'GPS','Balise GPS','Balise GPS','Balise GPS','Balise GPS','GEONATURE','129.001',true), 
            (129,2,'GSM','Balise GSM','Balise GSM (réseau mobile)','Balise GSM','Balise GSM (réseau mobile)','GEONATURE','129.002',true), 
            (129,3,'Argos','Balise Argos','Balise Argos','Balise Argos','Balise Argos','GEONATURE','129.003',true),
            (129,4,'VHF','Balise VHF','Balise VHF','Balise VHF','Balise VHF','GEONATURE','129.004',true)
            """
        )
    )

def downgrade():
    op.execute(f"DROP TRIGGER IF EXISTS tr_meta_dates_bib_tracking_devices ON {SCHEMA_NAME}.bib_tracking_devices;")
    op.execute(f"DROP FUNCTION IF EXISTS {SCHEMA_NAME}.set_meta_dates();")
    op.execute(f"DELETE FROM ref_nomenclatures.t_nomenclatures WHERE id_type = 129;")
    op.execute(f"DELETE FROM ref_nomenclatures.bib_nomenclatures_types WHERE id_type = 129;")
    op.drop_table("bib_tracking_devices", schema=SCHEMA_NAME)
