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
