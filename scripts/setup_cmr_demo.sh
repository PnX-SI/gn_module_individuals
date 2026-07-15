#!/usr/bin/env bash
set -euo pipefail

# Installe le sous-module Monitoring "CMR_BOUQUETIN" (démonstration CMR sur les
# bouquetins de la Vanoise), utilisé par les données de test de la migration
# individuals 0004_insert_test_data.
#
# Ce script est un prérequis manuel : le dossier de config d'un sous-module
# Monitoring doit être symlinké dans geonature/backend/media/monitorings/,
# un emplacement hors du contrôle de version. Il ne peut donc pas être fait
# depuis une migration alembic sans dépendance dure à gn_module_monitoring.
#
# Usage:
#   ./scripts/setup_cmr_demo.sh [GEONATURE_HOME] [GEONATURE_CONFIG_FILE]
#
# Prérequis : le venv GeoNature actif (commande `geonature` disponible) et
# le module gn_module_monitoring déjà installé (`geonature install-gn-module`).

GEONATURE_HOME="${1:-$HOME/geonature}"
GEONATURE_CONFIG_FILE="${2:-$GEONATURE_HOME/config/geonature_config.toml}"
MODULE_CODE="CMR_BOUQUETIN"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SRC="$SCRIPT_DIR/../backend/gn_module_individuals/migrations/data/cmr_bouquetin"
MONITORINGS_MEDIA_DIR="$GEONATURE_HOME/backend/media/monitorings"

if ! command -v geonature >/dev/null 2>&1; then
    echo "Erreur : commande 'geonature' introuvable. Activez le venv GeoNature avant de lancer ce script." >&2
    exit 1
fi

mkdir -p "$MONITORINGS_MEDIA_DIR"
ln -sfn "$CONFIG_SRC" "$MONITORINGS_MEDIA_DIR/$MODULE_CODE"

echo "Lien symbolique créé : $MONITORINGS_MEDIA_DIR/$MODULE_CODE -> $CONFIG_SRC"

# `geonature monitorings install` : on ne l'appelle donc que si le
# sous-module n'est pas déjà enregistré, pour pouvoir relancer ce script sans risque.
MODULE_EXISTS=$(
    GEONATURE_CONFIG_FILE="$GEONATURE_CONFIG_FILE" geonature db exec --json \
        "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = '$MODULE_CODE') AS e" \
        2>/dev/null | grep -o '"e": *true' || true
)

if [ -z "$MODULE_EXISTS" ]; then
    GEONATURE_CONFIG_FILE="$GEONATURE_CONFIG_FILE" geonature monitorings install "$MODULE_CODE"
else
    echo "Le sous-module $MODULE_CODE existe déjà, installation ignorée."
fi

echo "Attribution des permissions Grp_admin sur $MODULE_CODE et MONITORINGS..."

GEONATURE_CONFIG_FILE="$GEONATURE_CONFIG_FILE" geonature db exec --commit "
INSERT INTO gn_permissions.t_permissions (id_role, id_action, id_module, id_object, scope_value)
SELECT r.id_role, pa.id_action, pa.id_module, pa.id_object, NULL
FROM gn_permissions.t_permissions_available pa
JOIN gn_commons.t_modules m ON m.id_module = pa.id_module
JOIN utilisateurs.t_roles r ON r.nom_role = 'Grp_admin'
WHERE m.module_code IN ('$MODULE_CODE', 'MONITORINGS')
AND NOT EXISTS (
    SELECT 1 FROM gn_permissions.t_permissions p
    WHERE p.id_role = r.id_role
      AND p.id_action = pa.id_action
      AND p.id_module = pa.id_module
      AND p.id_object = pa.id_object
);
"

echo
echo "Sous-module $MODULE_CODE installé."
echo "Vous pouvez maintenant lancer 'geonature db upgrade individuals@head' pour charger les données de démonstration,"
echo "puis 'GEONATURE_CONFIG_FILE=$GEONATURE_CONFIG_FILE geonature monitorings synchronize_synthese $MODULE_CODE' pour synchroniser vers la synthèse."
