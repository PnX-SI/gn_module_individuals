"""Create tables

Revision ID: 0002_create_tables
Revises: 0001_init_migrations
Create Date: 2026-03-19 15:40:48.398854

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import select, table, column, functions as func

# revision identifiers, used by Alembic.
revision = "0002_create_tables"
down_revision = "0001_init_migrations"
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

    t_individual_deployments = op.create_table(
        "t_individual_deployments",
        sa.Column(
            "id_deployment",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "id_capture",
            sa.Integer(),
            # sa.ForeignKey("t_captures.id_capture"),
            nullable=False,
        ),
        sa.Column(
            "id_individual",
            sa.Integer(),
            sa.ForeignKey("gn_monitoring.t_individuals.id_individual"),
            nullable=False,
        ),
        sa.Column(
            "id_nomenclature_deployment_type",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "id_nomenclature_deployment_location",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "id_tracking_device",
            sa.Integer(),
            sa.ForeignKey("gn_individual.bib_tracking_devices.id_tracking_device"),
            nullable=True,
        ),
        sa.Column(
            "marking_code",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "install_date",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "removal_date",
            sa.DateTime(),
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

    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION {SCHEMA_NAME}.set_meta_dates()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                NEW.meta_create_date := NOW();
            ELSIF TG_OP = 'UPDATE' THEN
                NEW.meta_update_date := NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        f"""
        CREATE TRIGGER tr_meta_dates_bib_tracking_devices
        BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.bib_tracking_devices
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA_NAME}.set_meta_dates();
    """
    )

    op.execute(
        f"""
        CREATE TRIGGER tr_meta_dates_individual_deployments
        BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.t_individual_deployments
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA_NAME}.set_meta_dates();
    """
    )

    bib_nomencl = table(
        "bib_nomenclatures_types",
        column("id_type", sa.Integer),
        column("mnemonique", sa.String),
        column("label_default", sa.String),
        column("definition_default", sa.String),
        column("label_fr", sa.String),
        column("definition_fr", sa.String),
        column("source", sa.String),
        schema="ref_nomenclatures",
    )

    req_obj = select(func.max(bib_nomencl.c.id_type))
    last_value = conn.execute(req_obj).scalar()
    next_id = (last_value or 0) + 1

    op.execute(
        sa.insert(bib_nomencl).values(
            [
                {
                    "id_type": next_id,
                    "mnemonique": "TYPE_DISPO_SUIVI",
                    "label_default": "Type de dispositif de suivi",
                    "definition_default": "Dispositif de suivi",
                    "label_fr": "Type de dispositif de suivi",
                    "definition_fr": "Dispositif de suivi",
                    "source": "GEONATURE",
                },
            ]
        )
    )

    t_nomencl = table(
        "t_nomenclatures",
        column("id_type", sa.Integer),
        column("cd_nomenclature", sa.String),
        column("mnemonique", sa.String),
        column("label_default", sa.String),
        column("definition_default", sa.String),
        column("label_fr", sa.String),
        column("definition_fr", sa.String),
        column("source", sa.String),
        column("hierarchy", sa.String),
        column("active", sa.Boolean),
        schema="ref_nomenclatures",
    )

    op.execute(
        sa.insert(t_nomencl).values(
            [
                {
                    "id_type": next_id,
                    "cd_nomenclature": "1",
                    "mnemonique": "GPS",
                    "label_default": "Balise GPS",
                    "definition_default": "Balise GPS",
                    "label_fr": "Balise GPS",
                    "definition_fr": "Balise GPS",
                    "source": "GEONATURE",
                    "hierarchy": "129.001",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": "2",
                    "mnemonique": "GSM",
                    "label_default": "Balise GSM",
                    "definition_default": "Balise GSM",
                    "label_fr": "Balise GSM",
                    "definition_fr": "Balise GSM",
                    "source": "GEONATURE",
                    "hierarchy": "129.002",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": "3",
                    "mnemonique": "Argos",
                    "label_default": "Balise Argos",
                    "definition_default": "Balise Argos",
                    "label_fr": "Balise Argos",
                    "definition_fr": "Balise Argos",
                    "source": "GEONATURE",
                    "hierarchy": "129.003",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": "4",
                    "mnemonique": "VHF",
                    "label_default": "Balise VHF",
                    "definition_default": "Balise VHF",
                    "label_fr": "Balise VHF",
                    "definition_fr": "Balise VHF",
                    "source": "GEONATURE",
                    "hierarchy": "129.004",
                    "active": True,
                },
            ]
        )
    )

    # --- TYPE_MARQUAGE : type de marquage physique de l'animal ---
    op.execute(
        sa.insert(bib_nomencl).values(
            [
                {
                    "id_type": next_id + 1,
                    "mnemonique": "TYPE_MARQUAGE",
                    "label_default": "Type de marquage physique",
                    "definition_default": "Type de marquage physique apposé sur l'animal",
                    "label_fr": "Type de marquage physique",
                    "definition_fr": "Type de marquage physique apposé sur l'animal",
                    "source": "GEONATURE",
                },
            ]
        )
    )

    op.execute(
        sa.insert(t_nomencl).values(
            [
                {
                    "id_type": next_id + 1,
                    "cd_nomenclature": "1",
                    "mnemonique": "PLAQUE",
                    "label_default": "Plaque",
                    "definition_default": "Marque individuelle de type plaque (bague, plaque auriculaire…)",
                    "label_fr": "Plaque",
                    "definition_fr": "Marque individuelle de type plaque (bague, plaque auriculaire…)",
                    "source": "GEONATURE",
                    "hierarchy": "130.001",
                    "active": True,
                },
                {
                    "id_type": next_id + 1,
                    "cd_nomenclature": "2",
                    "mnemonique": "PEINTURE",
                    "label_default": "Peinture",
                    "definition_default": "Marque colorée à la peinture",
                    "label_fr": "Peinture",
                    "definition_fr": "Marque colorée à la peinture",
                    "source": "GEONATURE",
                    "hierarchy": "130.002",
                    "active": True,
                },
                {
                    "id_type": next_id + 1,
                    "cd_nomenclature": "3",
                    "mnemonique": "DECOLORATION",
                    "label_default": "Décoloration",
                    "definition_default": "Marque par décoloration du pelage ou du plumage",
                    "label_fr": "Décoloration",
                    "definition_fr": "Marque par décoloration du pelage ou du plumage",
                    "source": "GEONATURE",
                    "hierarchy": "130.003",
                    "active": True,
                },
                {
                    "id_type": next_id + 1,
                    "cd_nomenclature": "4",
                    "mnemonique": "DISPO_SUIVI",
                    "label_default": "Dispositif de suivi",
                    "definition_default": "Dispositif électronique de suivi (collier GPS, balise, émetteur…)",
                    "label_fr": "Dispositif de suivi",
                    "definition_fr": "Dispositif électronique de suivi (collier GPS, balise, émetteur…)",
                    "source": "GEONATURE",
                    "hierarchy": "130.004",
                    "active": True,
                },
            ]
        )
    )

    # --- LOC_MARQUAGE : localisation du marquage sur le corps de l'animal ---
    op.execute(
        sa.insert(bib_nomencl).values(
            [
                {
                    "id_type": next_id + 2,
                    "mnemonique": "LOC_MARQUAGE",
                    "label_default": "Localisation du marquage",
                    "definition_default": "Partie du corps où est apposé le marquage",
                    "label_fr": "Localisation du marquage",
                    "definition_fr": "Partie du corps où est apposé le marquage",
                    "source": "GEONATURE",
                },
            ]
        )
    )

    op.execute(
        sa.insert(t_nomencl).values(
            [
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "1",
                    "mnemonique": "OD_AV",
                    "label_default": "Oreille droite devant",
                    "definition_default": "Face antérieure de l'oreille droite",
                    "label_fr": "Oreille droite devant",
                    "definition_fr": "Face antérieure de l'oreille droite",
                    "source": "GEONATURE",
                    "hierarchy": "131.001",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "2",
                    "mnemonique": "OD_AR",
                    "label_default": "Oreille droite derrière",
                    "definition_default": "Face postérieure de l'oreille droite",
                    "label_fr": "Oreille droite derrière",
                    "definition_fr": "Face postérieure de l'oreille droite",
                    "source": "GEONATURE",
                    "hierarchy": "131.002",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "3",
                    "mnemonique": "OG_AV",
                    "label_default": "Oreille gauche devant",
                    "definition_default": "Face antérieure de l'oreille gauche",
                    "label_fr": "Oreille gauche devant",
                    "definition_fr": "Face antérieure de l'oreille gauche",
                    "source": "GEONATURE",
                    "hierarchy": "131.003",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "4",
                    "mnemonique": "OG_AR",
                    "label_default": "Oreille gauche derrière",
                    "definition_default": "Face postérieure de l'oreille gauche",
                    "label_fr": "Oreille gauche derrière",
                    "definition_fr": "Face postérieure de l'oreille gauche",
                    "source": "GEONATURE",
                    "hierarchy": "131.004",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "5",
                    "mnemonique": "ENCOLURE",
                    "label_default": "Encolure",
                    "definition_default": "Encolure (cou/nuque)",
                    "label_fr": "Encolure",
                    "definition_fr": "Encolure (cou/nuque)",
                    "source": "GEONATURE",
                    "hierarchy": "131.005",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "6",
                    "mnemonique": "DOS",
                    "label_default": "Dos",
                    "definition_default": "Région dorsale",
                    "label_fr": "Dos",
                    "definition_fr": "Région dorsale",
                    "source": "GEONATURE",
                    "hierarchy": "131.006",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "7",
                    "mnemonique": "PATTE_D",
                    "label_default": "Patte droite",
                    "definition_default": "Patte ou membre postérieur droit",
                    "label_fr": "Patte droite",
                    "definition_fr": "Patte ou membre postérieur droit",
                    "source": "GEONATURE",
                    "hierarchy": "131.007",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "8",
                    "mnemonique": "PATTE_G",
                    "label_default": "Patte gauche",
                    "definition_default": "Patte ou membre postérieur gauche",
                    "label_fr": "Patte gauche",
                    "definition_fr": "Patte ou membre postérieur gauche",
                    "source": "GEONATURE",
                    "hierarchy": "131.008",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "9",
                    "mnemonique": "AILE_D",
                    "label_default": "Aile droite",
                    "definition_default": "Aile droite (oiseaux)",
                    "label_fr": "Aile droite",
                    "definition_fr": "Aile droite (oiseaux)",
                    "source": "GEONATURE",
                    "hierarchy": "131.009",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "10",
                    "mnemonique": "AILE_G",
                    "label_default": "Aile gauche",
                    "definition_default": "Aile gauche (oiseaux)",
                    "label_fr": "Aile gauche",
                    "definition_fr": "Aile gauche (oiseaux)",
                    "source": "GEONATURE",
                    "hierarchy": "131.010",
                    "active": True,
                },
            ]
        )
    )


def downgrade():
    op.execute(
        f"DROP TRIGGER IF EXISTS tr_meta_dates_bib_tracking_devices ON {SCHEMA_NAME}.bib_tracking_devices;"
    )
    op.execute(
        f"DROP TRIGGER IF EXISTS tr_meta_dates_individual_deployments ON {SCHEMA_NAME}.t_individual_deployments;"
    )
    op.execute(f"DROP FUNCTION IF EXISTS {SCHEMA_NAME}.set_meta_dates();")
    op.drop_table("t_individual_deployments", schema=SCHEMA_NAME, if_exists=True)
    op.drop_table("bib_tracking_devices", schema=SCHEMA_NAME, if_exists=True)
    op.execute("""
        DELETE FROM ref_nomenclatures.t_nomenclatures t
        USING ref_nomenclatures.bib_nomenclatures_types b
        WHERE t.id_type = b.id_type
        AND b.mnemonique IN ('TYPE_DISPO_SUIVI', 'TYPE_MARQUAGE', 'LOC_MARQUAGE');
    """)
    op.execute("""
        DELETE FROM ref_nomenclatures.bib_nomenclatures_types
        WHERE mnemonique IN ('TYPE_DISPO_SUIVI', 'TYPE_MARQUAGE', 'LOC_MARQUAGE');
    """)
