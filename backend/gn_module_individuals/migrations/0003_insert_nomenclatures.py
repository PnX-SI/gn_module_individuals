"""Insert nomenclatures

Revision ID: 0003_insert_nomenclatures
Revises: 0002_create_tables
Create Date: 2026-07-13 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import select, table, column, functions as func

# revision identifiers, used by Alembic.
revision = "0003_insert_nomenclatures"
down_revision = "0002_create_tables"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
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

    # --- TYPE_MARQUAGE: physical marking type applied to the animal ---
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

    # --- LOC_MARQUAGE: marking location on the animal's body ---
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
                    "mnemonique": "OD",
                    "label_default": "Oreille droite",
                    "definition_default": "Oreille droite",
                    "label_fr": "Oreille droite",
                    "definition_fr": "Oreille droite",
                    "source": "GEONATURE",
                    "hierarchy": "131.001",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "2",
                    "mnemonique": "OG",
                    "label_default": "Oreille gauche",
                    "definition_default": "Oreille gauche",
                    "label_fr": "Oreille gauche",
                    "definition_fr": "Oreille gauche",
                    "source": "GEONATURE",
                    "hierarchy": "131.002",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "3",
                    "mnemonique": "ENCOLURE",
                    "label_default": "Encolure",
                    "definition_default": "Encolure (cou/nuque)",
                    "label_fr": "Encolure",
                    "definition_fr": "Encolure (cou/nuque)",
                    "source": "GEONATURE",
                    "hierarchy": "131.003",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "4",
                    "mnemonique": "DOS",
                    "label_default": "Dos",
                    "definition_default": "Région dorsale",
                    "label_fr": "Dos",
                    "definition_fr": "Région dorsale",
                    "source": "GEONATURE",
                    "hierarchy": "131.004",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "5",
                    "mnemonique": "PATTE_D",
                    "label_default": "Patte droite",
                    "definition_default": "Patte ou membre postérieur droit",
                    "label_fr": "Patte droite",
                    "definition_fr": "Patte ou membre postérieur droit",
                    "source": "GEONATURE",
                    "hierarchy": "131.005",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "6",
                    "mnemonique": "PATTE_G",
                    "label_default": "Patte gauche",
                    "definition_default": "Patte ou membre postérieur gauche",
                    "label_fr": "Patte gauche",
                    "definition_fr": "Patte ou membre postérieur gauche",
                    "source": "GEONATURE",
                    "hierarchy": "131.006",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "7",
                    "mnemonique": "AILE_D",
                    "label_default": "Aile droite",
                    "definition_default": "Aile droite (oiseaux)",
                    "label_fr": "Aile droite",
                    "definition_fr": "Aile droite (oiseaux)",
                    "source": "GEONATURE",
                    "hierarchy": "131.007",
                    "active": True,
                },
                {
                    "id_type": next_id + 2,
                    "cd_nomenclature": "8",
                    "mnemonique": "AILE_G",
                    "label_default": "Aile gauche",
                    "definition_default": "Aile gauche (oiseaux)",
                    "label_fr": "Aile gauche",
                    "definition_fr": "Aile gauche (oiseaux)",
                    "source": "GEONATURE",
                    "hierarchy": "131.008",
                    "active": True,
                },
            ]
        )
    )

    # The id_type values above are inserted explicitly (bypassing the sequence's
    # nextval), so it must be resynced — otherwise the next nomenclature type
    # inserted through the ORM (e.g. by another module) would collide with them.
    conn.execute(
        select(
            sa.func.setval(
                "ref_nomenclatures.bib_nomenclatures_types_id_type_seq",
                select(func.max(bib_nomencl.c.id_type)).scalar_subquery(),
            )
        )
    )


def downgrade():
    op.execute(
        """
        DELETE FROM ref_nomenclatures.t_nomenclatures t
        USING ref_nomenclatures.bib_nomenclatures_types b
        WHERE t.id_type = b.id_type
        AND b.mnemonique IN ('TYPE_DISPO_SUIVI', 'TYPE_MARQUAGE', 'LOC_MARQUAGE');
    """
    )
    op.execute(
        """
        DELETE FROM ref_nomenclatures.bib_nomenclatures_types
        WHERE mnemonique IN ('TYPE_DISPO_SUIVI', 'TYPE_MARQUAGE', 'LOC_MARQUAGE');
    """
    )
