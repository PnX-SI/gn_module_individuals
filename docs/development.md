# Doc du PNV pour le developement dans l'environnement de GeoNature

> L'idée de cette doc est de servir de mémo, de lister différentes astuces à destination des développeurs du module "individus".

- [Doc du PNV pour le developement dans l'environnement de GeoNature](#doc-du-pnv-pour-le-developement-dans-lenvironnement-de-geonature)
  - [Git / github](#git--github)
    - [`git stash`](#git-stash)
    - [Mettre à jour les infos du remote](#mettre-à-jour-les-infos-du-remote)
    - [Ajouter une modification au précédent commit](#ajouter-une-modification-au-précédent-commit)
    - [Associer une branche à un dépôt distant](#associer-une-branche-à-un-dépôt-distant)
    - [Créer une nouvelle branche à partir du remote](#créer-une-nouvelle-branche-à-partir-du-remote)
    - [Retirer des fichiers du commit](#retirer-des-fichiers-du-commit)
    - [Cloner une branche spécifique](#cloner-une-branche-spécifique)
    - [Renommer une branche](#renommer-une-branche)
    - ["Merge" sur la branche de confiance](#merge-sur-la-branche-de-confiance)
  - [Backend](#backend)
    - [Accès aux variables de configuration du module](#accès-aux-variables-de-configuration-du-module)
    - [Logs](#logs)
    - [Alembic](#alembic)
      - [Etat des migrations](#etat-des-migrations)
      - [Générer un nouveau fichier de version](#générer-un-nouveau-fichier-de-version)
      - [Soumettre ou retirer une révision](#soumettre-ou-retirer-une-révision)
    - [SQLAlchemy](#sqlalchemy)
      - [`scalars()`](#scalars)
      - [`@hybrid_property`](#hybrid_property)
    - [Sérialiser](#sérialiser)
      - [Sans marshmallow](#sans-marshmallow)
      - [Avec marshmallow](#avec-marshmallow)
        - [Exemple de sérialisation avec un schéma marshmallow](#exemple-de-sérialisation-avec-un-schéma-marshmallow)
        - [Utilisation de `Method()` dans le schema](#utilisation-de-method-dans-le-schema)
        - [Validation d'une donnée dans le schéma](#validation-dune-donnée-dans-le-schéma)
        - [Mixin or not ?](#mixin-or-not-)
  - [Frontend](#frontend)
    - [Utilisation des variables de configuration du module](#utilisation-des-variables-de-configuration-du-module)
    - [Mécanisme de traduction](#mécanisme-de-traduction)
      - [Configuration de `gnModule.module.ts`](#configuration-de-gnmodulemodulets)
      - [Utilisation du pipe de traduction](#utilisation-du-pipe-de-traduction)

## Git / github

### `git stash`

Permet de sauvegarder temporairement les modifications si l'on ne souhaite pas tout de suite les ajouter à un `commit`.

Exemple, je suis sur la branche feat/feat-3 et je souhaite faire un fetch sur ma branche develop sans ajouter mes dernières modifs à un commit et sans les perdre :

```shell
git stash
git checkout develop
git fetch github-pnv
git pull
git checkout feat/demoCynt
```

Pour récupérer les dernières modificaions stockées dans le stash :

```shell
git stash pop
```
### Mettre à jour les infos du remote

Cette commande permet de mettre à jour les infos du remote en supprimant les références locales aux branches distantes qui n’existent plus

```sh
git fetch --prune
```

### Ajouter une modification au précédent commit

Cela évite de refaire un commit lorsque c'est un oubli de sauvegarde ou modification qui concerne le précédent commit :

```sh
git commit --amend --no-edit
git push --force-with-lease <remote-alias> <branch>
```

### Associer une branche à un dépôt distant

Afin de ne pas avoir à systématiquement spécifier le dépôt distant concerné par les commandes `git fetch`, `git pull`, `git push`, il est possible d'associer à une branche un dépôt distant par défaut avec la commande :

```shell
git branch -u github-pnv/develop develop
```

l'option `-u <upstream>` est un racoursi de l'option `--set-upstream-to=<upstream>`
Dans cet exemple on paramètre la brache develop pour suivre la branche 'github-pnv/develop'

### Créer une nouvelle branche à partir du remote

Exemple :

```sh
git checkout -b fix/devicesList origin/develop
```

### Retirer des fichiers du commit

Vous souhaitez par exemple retirer des fichiers nouvellement créés que vous avez malencontreusement ajouté avec la commande `git add`. Ne faites pas encore de commit !

```shell
git restore --staged . 
```

Cette commande retire tous les fichiers ajoutés, pour spécifier un fichier en particulier il faut le préciser à l'option `-staged` à la place du '.'.

Vous pourez ensuite si vous le souhaitez rajouter ces fichier au `.gitignore`. Le `git status` ne devrait alors plus les mentionner.

Vous pouvez ensuite rajouter les fichier voulus au commit et créé votre commit.

```shell
git add <file>
git commit -m <message>
```

### Cloner une branche spécifique

Clone du dépôt + checkout
```sh
git clone <URL_DEPOT>
git checkout <branche>
```

Clone directement de la branche concernée
```sh
git clone -b <branche> --single-branch <URL_DEPOT>
```

### Renommer une branche

Renommer en local :

```sh
git branch -m <old_branch> <new_branch>
```

Supprimer la branche qui avait été poussée

```sh
git push origin --delete <old_branch>
```

Repousser la nouvelle branche, qui sera créée sur le répo distant :

```sh
git push --set-upstream origin <new_branch>
```

### "Merge" d'une branche fonctionelle sur la branche de confiance

Pour l'exemple, `develop` est la branche de confiance et `feat/dev` la branche à merger. Nous souhaiterions réaliser ce merge via une PR.

Il est préférable pour ne pas faire d'erreur de ne pas avoir de branche develop en local, la surprimer :

```sh
git branch -D develop
```

#### Mise à jour de la branche `feat/dev` en local

```sh
git fetch origin
git checkout feat/dev
git pull
```

#### Rebaser la branche avec `develop` du remote

```sh
git merge develop
```

#### Résolution des conflits et `push`

S'il y a des conflits, les résoudre en modifiant les fichiers et en les sauvegardant. Puis

```sh
git add .
git commit -m "chore: resolve rebase conflicts"
git rebase --continue
git push
```

#### Création d'une PR sur github

Crééer une PR qui compare `feat/dev` à `develop`.
Si vous êtes admin du répo, merger la PR puis supprimer la branche `feat/dev`.

#### Mise à jour des références locales

Pour tout le monde :

```sh
git fetch --prune
```

#### Les autres développeurs

!!! Les autres développeurs, après le rebase

```sh
git fetch origin
git rebase origin/feat/dev
```

### Bonnes pratiques de dev

#### Avant de reprendre une session de code (matin)

```sh
git fetch origin
git checkout <ma_branche>
git pull
git rebase origin/develop
git status
```

Puis dev

#### A la fin d'une session de code (soir)

```sh
git fetch origin
git add <liste_des_fichiers>
git commit -m "<msg>"
git push --force with-lease
```

## Backend

### Accès aux variables de configuration du module

Le fichier de configuration, `individuals_config.toml` doit soit être place dans `~/geonature/config` (pour la prod), soit un lien symbolique doit être créé dans ce dossier depuis `~/gn_module_individuals/individuals_config.toml` (plus pratique pour le dev).

```sh
ln -s ~/gn_module_individuals/individuals_config.toml  ~/geonature/config/individuals_config.toml
```

Le fichier `~/gn_module_individuals/backend/conf_shema.py` doit être créé et doit déclarer toutes les variables possibles pour le modul

```python
from marshmallow import Schema, fields

class GnModuleSchemaConf(Schema):
    TEST_VAR = fields.String(load_default="Bonjour")
```

Les variables non déclarées ici ne pourront pas être surcouchées via le fichier `.toml`.

### Logs

Pour insérer les logs dans les fichiers de log `/var/log/geonature/geonature.log`

```python
import logging
logger = logging.getLogger(__name__)

[...]

logger.info("SQL: %s", sql) # ou logger.debug selon le niveau souhaité
```

### Alembic

#### Etat des migrations

```shell
# Etat de toute la BDD
geonature db status

# Etat d'une branche de la BDD
geonature db status <branch_name>
```

#### Générer un nouveau fichier de version

```shell
geonature db revision -m "<revision_name>" --head <branch_name>@head
```

L'option `--head` indique à partir de quel endroit de l'arbre des révisions doit être appliquée celle-ci. Par exemple, la valeur `demo@head`, indique qu'elle doit être appliquée à la tête de la branche `demo` (en dernier).

Cette commande crée donc le fichier `.../revisions/<serial>_<revision_name>.py`.

> [!NOTE]
> Pour la 1ère révision d'un modèle, il est impératif de préciser l'option `--branch-label <nom_branche>` afin que la variable `branch_labels` du fichier de migration soit renseigné (cela pouvant être fait à postériori directement dans le fichier avant de soumettre la migration à alembic).

#### Soumettre ou retirer une révision

Cette commande applique la dernière migration en jouant la fonction python `upgrade()` :

```shell
geonature db upgrade <branch_name>@head
```

Cette commande retire la dernière migration en jouant la fonction python `downgrade()` de la dernière migration appliquée:

```shell
geonature db downgrade <branch_name>@-1
```


### SQLAlchemy

#### `scalars()`

Cette fonction permet de retourner les objets du modèle et non des dictionnaires

```python
## ----- blueprint.py
indivs = db.session.execute(query).scalars().all()
```

Idem que

```python
indivs = db.session.scalars(query).unique().all()
```

#### `@hybrid_property`

Pour que le champ d'un modèle soit le résultat de l'appel à une fonction :

```python
# ----- models.py
class Individual(DB.Model):
    [...]
    @hybrid_property
    def nom_complet(self):
        return self.taxref.nom_complet if self.taxref else None
```

### Sérialiser

#### Sans marshmallow

> [!WARNING]
> A ne plus utiliser : Méthode dépréciée pour GeoNature, seule la sérialisation avec marshmallow est acceptée !**

```python
@blueprint.route("/indiv", methods=["GET"])
@login_required
@json_resp
def indiv():
    query = db.select(
                Individual.id_individual,
                Individual.name,
                Taxref.nom_complet
             ).select_from(Individual).join(Taxref, Individual.cd_nom == Taxref.cd_nom)
    indivs = db.session.execute(query).all()

    return [{"id_individual": indiv.id_individual, "name": indiv.name, "nom_complet": indiv.nom_complet} for indiv in indivs]
```

#### Avec marshmallow

> [!NOTE]
> La sérialisation avec marshmallow est la méthode recommandée par la communauté GeoNature.

##### Exemple de sérialisation avec un schéma marshmallow

```python
## ----- shemas.py
from geonature.utils.env import ma
[...]

class IndividualSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Individual
        include_fk = True
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    taxref = ma.Nested(TaxrefSchema)

## ----- blueprint.py
@blueprint.route("/indiv/<int(signed=True):id_individual>", methods=["GET"])
@login_required
@json_resp
def indiv(id_individual):
    # Un schéma doit être créé
    schema = IndividualSchema(many=True)

    query = (
        db.select(Individual)
        .options(joinedload(Individual.taxref))
        .filter_by(id_individual=id_individual)
    )

    indivs = db.session.execute(query).one_or_none()

    # Sérialisation
    return schema.dump(indivs)
```

##### Utilisation de `Method()` dans le schema

```python
## ----- shemas.py
class IndividualSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        [...]

    # Si on ne veut pas le taxref imbriqué mais directement le nom_complet
    nom_complet = fields.Method("get_nom_complet")

    def get_nom_complet(self, obj):
        return obj.taxref.nom_complet if obj.taxref else None
```

##### Validation d'une donnée dans le schéma

```python
ADDITIONAL_DATA_ALLOWED_KEYS = ["collier", "taille_cm"]

class IndividualSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        [...]

    # Mise en place d'une validation sur le champ addtional_data
    @validates("additional_data")
    def validates_additional_data(self, additional_data):

        # Test du type de donnée
        if additional_data is not None and not isinstance(additional_data, dict):
            raise ValidationError("additional_data must be a JSON object (dict).")

        # Test de la valeur des champs : au moins tous les champs de ADDITIONAL_DATA_ALLOWED_KEYS doivent être définis
        if not all(field in additional_data.keys() for field in ADDITIONAL_DATA_ALLOWED_KEYS):
            raise ValidationError(
                f"additional_data must contains these fields: {ADDITIONAL_DATA_ALLOWED_KEYS}."
            )

        # Tester si le cd_nom de additionnal_data existe dans Taxref
        cd_nom_payload = additional_data.get("cd_nom")
        if cd_nom_payload is not None:
            cd_nom_additional = db.session.execute(
                db.select(Taxref).filter_by(cd_nom=cd_nom_payload)
            ).scalars.one_or_none()

            if cd_nom_additional is None:
                raise ValidationError(
                    f"cd_nom {cd_nom_payload} in additional_data does not exist in taxref."
                )
            return additional_data
```

##### Mixin or not ?

`SmartRelationshipsMixin` force à ne pas charger les relations ships et c'est cette méthode qui est préconisée par les mainteneurs de GeoNature. (cf <https://docs.geonature.fr/development.html#gestion-des-relationships>).

Les 2 exemples suivants démontrent comment utiliser 2 méthodes pour sérialiser le champ `taxref` du model `Individual` qui est une relationship définie par la ForeignKey sur le champ `cd_nom`

Exemple avec l'utilisation du Mixin :

```python
## ----- shemas.py
class IndividualSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Individual
        include_fk = True
        load_instance = True
        sqla_session = db.session

    taxref = ma.Nested(TaxrefSchema)

## ----- models.py
class Individual(DB.Model):
    __tablename__ = "t_individuals"
    __table_args__ = {"schema": SCHEMA_NAME}

    id_individual = DB.Column(
        "id_individual",
        DB.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = DB.Column(
        "name",
        DB.Text,
        nullable=True,
    )

    cd_nom = DB.Column("cd_nom", DB.Integer, DB.ForeignKey(Taxref.cd_nom))

    additional_data = DB.Column(
        "additional_data",
        JSONB,
        nullable=True,
        server_default="{}",
    )

    taxref = DB.relationship(
        Taxref,
        lazy="joined",
        viewonly=True,
    )

## ----- blueprint.py
@blueprint.route("/indiv", methods=["GET"])
@login_required
@json_resp
def list_indiv():
    # C'est ce paramètre "only" qui fait toute la différence !
    schema = IndividualSchema(many=True, only=["taxref"])

    query = db.select(Individual).options(joinedload(Individual.taxref))

    indivs = db.session.execute(query).scalars().all()

    return schema.dump(indivs)
```

Exemple sans l'utilisation du Mixin :

```python
## ----- shemas.py
# On retire le Mixin
class IndividualSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Individual
        include_fk = True
        load_instance = True
        sqla_session = db.session

    taxref = ma.Nested(TaxrefSchema)

## ----- models.py
# Rien ne change côté model

## ----- blueprint.py
@blueprint.route("/indiv", methods=["GET"])
@login_required
@json_resp
def list_indiv():
    # On retire le paramètre "only"
    schema = IndividualSchema(many=True)

    query = db.select(Individual).options(joinedload(Individual.taxref))

    indivs = db.session.execute(query).scalars().all()

    return schema.dump(indivs)
```

### Tests

Pour avoir une idée du coverage avant de faire la pull request, lancer avec le venv activé

```
  pytest -v --cov --cov-report=term-missing
```

## Frontend

### Utilisation des variables de configuration du module

Pour cela il faut initialiser le contructeur du composant principal comme cela :

```typescript
import { ConfigService } from '@geonature/services/config.service';

export class TabComponent implements OnInit {
  
    constructor(
        private config: ConfigService,
    ) {}
}
```

Puis appeler la variable souhaitée, comme par exemple :

```typescript
ngOnInit() {
    console.log('Config:', this.config["INDIVIDUALS"]["TEST_VAR"]);
}
```

### Mécanisme de traduction

#### Configuration de `gnModule.module.ts`

Créer une fonction qui permet de charger les fichiers de traduction json et importer l'ensemble des modules nécessaires à la mise en place du mécanisme de traduction.

```typescript
import { CustomTranslateLoader } from '@geonature/shared/translate/custom-loader';
import { TranslateModule, TranslateLoader, TranslateService } from '@ngx-translate/core';
import { I18nService } from '@geonature/shared/translate/i18n-service';

[...]

export function createTranslateLoader(http: HttpClient, config: cs) {
    return new CustomTranslateLoader(http, config, { moduleName: 'individuals' });
}
```

`CustomTranslateLoder` est une fonction qui va charger, en fonction du nom du module et de la langue par défaut configurée dans GeoNature (DEFAULT_LANGUAGE), le fichier situé dans {nom_du_module}/frontend/assets/i18n/{langue}.json

Importer ensuite le module `TranslateModule` comme suit :

```typescript
TranslateModule.forChild({
    loader: {
        provide: TranslateLoader,
        useFactory: createTranslateLoader,
        deps: [HttpClient, cs],
    },
    isolate: true,
}),
```

Afin que les LazyModule (chargés à la volée en fonction des besoins) bénéficient, à leur chargement, du service de traduction, il est nécessaire d'initialiser le constructeur de `GeonatureModule` comme suit :

```typescript
export class GeonatureModule {
    constructor(
        private translateService: TranslateService,
        private i18nService: I18nService
    ) {
        this.i18nService.initializeModuleTranslateService(this.translateService);
    }
}
```

#### Utilisation du pipe de traduction

Ensuite, dans tous les composants déclarés dans le `@NgModule`, utiliser la fonction de traduction comme suit :

```html
<span>{{ 'Individuals.NavigationTabs.Individuals' | translate }}</span>
```

`Individuals.NavigationTabs.Individuals` correspond ici à l'attribut `"Individuals" : { NavigationTabs": {"Individuals":""}}` du fichier assets/i18n/{langue}.json
