# Module Individuals

[![codecov](https://codecov.io/gh/PnX-SI/gn_module_individuals/branch/master/graph/badge.svg)](https://codecov.io/gh/PnX-SI/gn_module_individuals)

## Données de test

Les données de démonstration (individus, dispositifs, relevés Occtax de test)
vivent dans une branche Alembic dédiée, `individuals-samples`, séparée de la
branche principale `individuals`. Elle n'est donc jamais appliquée par
`geonature db autoupgrade`. Pour l'installer :

```bash
GEONATURE_CONFIG_FILE=... geonature db upgrade individuals-samples@head
```
