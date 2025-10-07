
::: {.introchapitre}
Comment structurer et renseigner les informations nécessaires à la création d'un livre avec le Pressoir.
:::


## Structure du livre

Pour créer un ouvrage avec le Pressoir, il est nécessaire de partir d'un dossier structuré dans lequel pourront être ajoutés les textes, les métadonnées et les références bibliographiques. C'est également dans ce dossier que le Pressoir générera les fichiers de configuration ainsi que les fichiers html.

Le Pressoir propose un modèle de livre, soit un squelette, prêt à remplir et commenté, qui comprend l'ensemble des dossiers et fichiers nécessaires à la production d'un livre[^1]. Ce modèle peut être modifié et adapté en fonction des besoins.

Il est également possible de créer son propre dossier.


### Fichiers source du livre

Les fichiers source du futur livre doivent être structurés comme suit&nbsp;:

1. Un dossier (ex&nbsp;: `MonLivre`) avec un sous-dossier `textes` dans lequel seront regroupées toutes les sources du livre.

2. Dans `textes` doivent figurer les éléments suivants&nbsp;:

    - un sous-dossier `garde` (pour la page de présentation du livre),
    - un sous-dossier par page (ou chapitre),
    - un sous-dossier `media`.

3. Dans `garde`, deux fichiers serviront à produire la page de présentation du livre&nbsp;:

    - un fichier yaml (les métadonnées) - `livre.yaml`
    - un fichier markdown (le texte) - `homepage.md`

4. Chaque sous-dossier chapitre se compose de deux à quatre fichiers&nbsp;:

    - un fichier yaml (les métadonnées) - ex&nbsp;: `chapitre1.yaml`
    - un fichier markdown (le texte) - ex&nbsp;: `chapitre1.md`
    - optionnellement, un fichier bibtex (la bibliographie structurée) - ex&nbsp;: `chapitre1.bib`
    - un quatrième fichier nommé `additionnels.md` est nécessaire pour l'ajout de contenus additionnels[^2].

5. Dans `media` seront regroupés l'ensemble des fichiers (illustration, document, vidéo...) utilisés dans le livre.

!contenuadd(./exempleArborescence)




### Fichiers créés par le Pressoir


[À l'instant où le livre est produit avec le Pressoir](chapitre1.html#construire-un-livre), un sous-dossier `pressoir` est automatiquement créé dans le dossier `MonLivre`. Il comprend&nbsp;:

- un dossier `static` constitué de quatre sous-dossiers (`css`, `fonts`, `js` et `svg`)

- un fichier `book.toml`

Ces fichiers de configuration pourront ensuite être modifiés afin de personnaliser l'ouvrage.



## Syntaxes utilisées

### Markdown

Tous les textes du livre doivent être rédigés selon les principes de la syntaxe markdown.

[Pour en savoir plus sur la syntaxe markdown](https://stylo-doc.ecrituresnumeriques.ca/fr/tutoriels/syntaxemarkdown/).

<!--
Préciser les spécificités en exemple : épigraphe, tableau, titre niveau 1
-->

### Yaml

Dans les fichiers yaml sont renseignées les métadonnées du livre et des chapitres. Elles sont indispensables à la production du livre.

[Pour en savoir plus sur la syntaxe yaml](https://stylo-doc.ecrituresnumeriques.ca/fr/tutoriels/syntaxe-yaml/).


Si les fichiers yaml ne sont pas correctement remplis, la production des html peut être entravée.

!contenuadd(./verificationYaml)



Le fichier `livre.yaml` comprend les métadonnées propres à l'ouvrage&nbsp;: titre, auteur, résumé, ISBN, [table des matières](chapitre4.html#structurer-la-table-des-matieres)...

!contenuadd(./yamldulivrevide)

!contenuadd(./yamldulivrecommente)




Le fichier `chapitreX.yaml` comprend les métadonnées propres à chaque chapitre&nbsp;: titre, sous-titre, auteur, résumé...

!contenuadd(./yamlduchapitrevide)

!contenuadd(./yamlduchapitrecommente)


Dans ces deux fichiers, certaines clés sont optionnelles et peuvent ou non être renseignées selon les besoins et spécificités de l'ouvrage, comme par exemple : `series`, `url_traduction`, `translators`, `zoterollection`...

### Bibtex

La syntaxe bibtex a pour fonction de structurer les références bibliographiques.

Elle permet la citation des références au sein du texte (grâce aux clés bibtex) et l'affichage de bibliographies mises en forme, en fin de chapitre ou sur une page dédiée.

[Pour en savoir plus sur la syntaxe Bibtex](https://stylo-doc.ecrituresnumeriques.ca/fr/tutoriels/syntaxe-bibtex/).

Les références bibliographiques, structurées au format bibtex, doivent figurer dans le fichier .bib&nbsp;:

- les références du `chapitre1` doivent être déposées dans le fichier `chapitre1.bib` afin de générer la bibliographie du chapitre.
- les références du livre doivent être regroupées dans `bibliographie/bibliographie.bib` pour constituer la bibliographie du livre[^3]. Le fichier `bibliographie.md` reste vide par défaut. Si un texte y est ajouté, il apparaîtra en tête de page, avant la liste des références, au moment de la publication.

Pour afficher la liste mise en forme de l'ensemble des références bibliographiques présentes dans le fichier .bib d'un chapitre, ajouter `Références`, en titre de niveau 2, à la fin du fichier .md correspondant. Par défaut, le style bibliographique est Chicago.


Pour afficher uniquement les références bibliographiques citées (celles dont la clé bibtex a été insérée dans le fichier .md), ajouter dans le fichier de métadonnées .yaml correspondant la clé et l'information suivantes&nbsp;:

```

nocite: '@*'

```

Lorsque la clé `zoterocollection` est renseigné dans le yaml du chapitre, un lien vers la collection Zotero du chapitre apparaît sous le titre de niveau 2 `Références`, une fois son contenu déployé.

![](./media/IllustrationZoteroCollection.png)

## Modèle par défaut

Le livre obtenu correspond à un modèle par défaut défini et appliqué par le Pressoir. Il est composé d'une [page de présentation](index.html) --&nbsp;qui correspond à la couverture du livre&nbsp;-- puis d'une liseuse où chaque page correspond à un chapitre de l'ouvrage créé.

Les éléments de navigation permettant de passer d'une page à une autre se situent dans le _header_ et le _footer_ présents sur toutes les pages de la liseuse.
Dans le _header_, un menu déroulant donne accès à la table des matières complète du livre.

Le corps de texte est mis en page selon le [style Tufte](https://edwardtufte.github.io/tufte-css/){link-archive="https://web.archive.org/web/20241003155835/https://edwardtufte.github.io/tufte-css/"}, avec la police de caractère Jannon.
Chaque page se présente sous forme de trois colonnes&nbsp;:

1. la table des matières du chapitre,
2. le texte,
3. le bloc de citation et les notes.

L'outil d'annotation [Hypothes.is](https://web.hypothes.is/) est présent dans une quatrième colonne, lorsque déployé (cf. les trois pictogrammes présents en haut de page, à droite du _header_).

![Pictogrammes de l'outil d'annotation Hypothes.is](media/PictoHypothesis.png)

Tous ces paramètres peuvent être [personnalisés](chapitre3.html).




[^1]: Voir le chapitre [«Prise en main»](chapitre1.html#initialiser-un-livre).

[^2]: Les contenus additionnels sont une fonctionnalité expliquée [ici](chapitre4.html#contenus-additionnels).

[^3]: Voir en exemple la [bibliographie](bibliographie.html) présente à la fin de cette documentation et qui recense l'ensemble des ouvrages publiés avec le Pressoir.
