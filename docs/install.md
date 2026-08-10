# Installation du module gn_module_individuals

## Prérequis
Disposer d'une instance de GeoNature >= 2.17
Disposer de UsersHub

## Installation

Récupérer les sources sur Github

```
git clone https://github.com/PnX-SI/gn_module_individuals.git
```

Puis installation du module :

```
source ~/geonature/backend/venv/bin/activate
geonature install-gn-module ~/gn_module_individuals
```

Donner tous les droits sur le module au groupe admin (Grp_admin) :

```
geonature permissions supergrant --nom Grp_admin --yes
```

Il faudra ensuite donner les droits souhaités aux utilisateurs via l'interface d'administration.

## Configuration

Pour pouvoir activer les champs additionels rajouter les paramètres suivant au fichier `geonature_config.toml`

```
# Champs additionnels
[ADDITIONAL_FIELDS]
    IMPLEMENTED_MODULES = ["OCCTAX", "METADATA", "INDIVIDUALS"]
    IMPLEMENTED_OBJECTS = ["OCCTAX_RELEVE", "OCCTAX_OCCURENCE", "OCCTAX_DENOMBREMENT", "METADATA_CADRE_ACQUISITION", "METADATA_JEU_DE_DONNEES", "INDIVIDUALS"]
```

## Données de test

Les données de démonstration (individus, dispositifs, relevés Occtax de test)
vivent dans une branche Alembic dédiée, `individuals-samples`, séparée de la
branche principale `individuals`. Elle n'est donc jamais appliquée par
`geonature db autoupgrade`. Pour l'installer :

```bash
GEONATURE_CONFIG_FILE=... geonature db upgrade individuals-samples@head
```