<!--

- en attente des modifs de David pour personnaliser les index au complet (picto inclus) directement dans book.toml.
- est-ce que je rapatrie sur cette page les personnalisation édito de type livre co, parties dans la toc... ? (cf. Antoine)

-->

::: {.introchapitre}
Modifier les paramètres par défaut pour personnaliser le livre créé.
:::


Par défaut, un ensemble de choix, graphiques et éditoriaux, ont été faits et sont appliqués par le Pressoir. Les paramètres peuvent être personnalisés en modifiant les fichiers présents dans le dossier `pressoir` et/ou les informations dans le fichier `book.toml`, comme par exemple&nbsp;: ajouter un logo, changer la police, modifier les couleurs, définir les termes à afficher dans l'index...



## Ajouter un logo


Un emplacement est prévu pour l'ajout d'un logo en haut à gauche du _header_ (ici **+ LE PRESSOIR +**, cf. `pressoir/static/img/pressoir-logo.png`).


Pour remplacer le logo par défaut, aller dans `pressoir/book.toml` et, dans la section `[theme]`, ajouter ou modifier les informations suivantes&nbsp;:

```
[theme]
logo-url = ['url("./img/pressoir-logo.png")', 'url("./img/mon-logo.png")']
```

Le fichier du logo doit être au format png.


## Lien sur le logo

Par défaut le lien sur le logo renvoie à la racine du (sous-)domaine, mais il est possible de spécifier une autre adresse.
Par exemple si le livre est servi à l'adresse `pressoir.org/livres/le-livre` mais que la présentation de la structure d'édition est à l'adresse `edition.org`, il peut être pertinent de modifier ce paramètre.
Il faut ajouter un paramètre `url_publisher` dans le fichier `textes/garde/livre.yaml` :

```
url_publisher: 'https://edition.org'
```


## Modifier la police

Les polices choisies doivent être déposées dans `pressoir/static/fonts` puis référencées dans `pressoir/static/css/fonts.css`.


!contenuadd(./parametragePolices)



## Choisir les couleurs

Les couleurs (_header_ et _footer_, table des matières, contenus additionnels...) peuvent être définies dans la section `[theme]` du fichier `book.toml`.

!contenuadd(./parametrageCouleurs)


## Définir l'index

Un index est un objet éditorial, sur une page dédiée (`textes/index/index-np.md`), qui présente une liste de termes classés par ordre alphabétique et qui renvoie aux endroits où ces termes sont cités tout au long du texte. Un index peut être constitué de plusieurs catégories.

Exemples de catégorie&nbsp;: Personnalités, Lieux, Organismes, Concepts...

L'index utilise le [balisage infra-textuel](chapitre4.html#balisage-infra-textuel).

Au préalable, il est nécessaire de déclarer, dans la section `[indexes]` du fichier `book.toml`&nbsp;:

- les étiquettes de balise (`ids`),
- le nom des catégories qui leur seront associées (`names`),
- le pictogramme qui les représentera (`images`).

!contenuadd(./parametrageIndex)

L'étiquette de balise (`ids`) ne sera pas visible pour les lecteur.rice.s. Elle ne doit pas comporter d'accent ou d'espace (ex&nbsp;: `personnalite`).

Le nom de chaque catégorie (`names`) sera visible par tou.te.s sur la page «&nbsp;Index&nbsp;» du livre produit (ex&nbsp;: Personnalités).

Le pictogramme, en .svg, doit être déposé dans le dossier `pressoir/static/svg`. Il apparaît dans le volet Index, à gauche du terme balisé, accessible via le [+] présent dans le corps du texte[^1].


!contenuadd(./ExemplePictoBalise)


## Pour aller plus loin

Pour aller plus loin dans la personnalisation graphique de l'ouvrage, modifier autant que souhaité les paramètres définis dans le fichier `pressoir/static/css/custom.css`.


[^1]: [Voir la section «&nbsp;Balisage infra-textuel&nbsp;» du chapitre «&nbsp;Personnalisation&nbsp;»](chapitre4.html#balisage-infra-textuel).
