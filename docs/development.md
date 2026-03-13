# Doc du PNV pour le developement dans l'environnement de GeoNature

L'idée de cette doc est de servir de mémo, de lister différentes astuces ...

## Git / github

### `git stash`

Permet de sauvegarder temporairement les modifications si l'on ne souhaite pas tout de suite les ajouter à un `commit`.

Exemple, je suis sur la branche feat/feat-3 et je souhaite faire un fetch sur ma branche develop sans ajouter mes dernières modifs à un comit et sans les perdre :

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

### Associer une branche à un dépôt distant

Afin de ne pas avoir à systématiquement spécifier le dépôt distant concerné par les commandes `git fetch`, `git pull`, `git push`, il est possible d'associer à une branche un dépôt distant par défaut avec la commande :

```shell
git branch -u github-pnv/develop develop
```

l'option `-u <upstream>` est un racoursi de l'option `--set-upstream-to=<upstream>`
Dans cet exemple on paramètre la brache develop pour suivre la branche 'github-pnv/develop'

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

## Backend

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

## Frontend

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

Afin que les LazyModule (chargés à la volée en fonction des besoins) bénéficient, à leur chargement, du service de traduction, il est nécessaire d'nitialiser le constructeur de `GeonatureModule` comme suit :

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