<!--

- Expliquer où et comment définir une nouvelle balise (non déjà existante) - notamment ajouter un nouveau picto pour une nouvelle balise (en attente développement David - cf. chapitre3).

- Est-il utile ou nécessaire de développer d'autres sujets ? (cf. Antoine)
        - insérer un tableau ? liens internes ?
        - Page de présentation du livre ?
        - Produire les book.tex et book.md ?
-->


::: {.introchapitre}
[Plusieurs](#styler-une-introduction-de-chapitre) fonctionnalités ont, au fur et à mesure, été développées pour le Pressoir, en fonction des besoins et des expérimentations des différents projets. Leur mode de fonctionnement est expliqué ci-dessous.
:::


## Structurer la table des matières

La table des matières, soit l'ordre et la structure des pages ou chapitres, est définie dans le fichier `livre.yaml`, avec la clé `toc`.

Chaque page est citée, avec son identifiant (`id`), dans l'ordre où elle doit apparaître.

```
toc:
    - id: introduction
    - id: chapitre1
    - id: chapitre2
    - id: chapitre3
    - id: chapitre4
    - id: conclusion
    - id: bibliographie
    - id: index-np
```

Si le livre comporte des parties, c'est-à-dire des regroupements de chapitres, les indiquer comme suit&nbsp;:

```
toc:
    - id: introduction
    - parttitle: titre de la Partie I
      content:
        - id: chapitre1
        - id: chapitre2
    - parttitle: titre de la Partie II
      content:
        - id: chapitre3
        - id: chapitre4
    - id: conclusion
    - id: bibliographie
    - id: index-np
```

Ces parties seront visibles dans le _header_, dans le menu déroulant présentant la table des matières au complet.


## Structurer un chapitre

Le titre de niveau 1 (`#`) correspond au titre du chapitre. Il doit être renseigné dans le yaml du chapitre. Par exemple, pour ce chapitre&nbsp;:

```
title: Fonctionnalités
```

Dans le fichier markdown, les titres commencent au niveau 2 (`##`) et suivants (`###`...).


À la fin du chapitre, deux titres de niveau 2 (`##`) peuvent être ajoutés&nbsp;:

- `Références`. C'est sous ce titre que s'affichera, lors de la visualisation en html, la bibliographie déclarée dans le fichier .bib du chapitre[^6].

- `Contenus additionnels`, sous lequel pourront être listés les contenus additionnels du chapitre[^5].



## Afficher ou non le nom de l'auteur.rice

Par défaut, le nom de l'auteur.rice, tel que défini dans le yaml du chapitre, apparaît sous le titre du chapitre en cours de lecture.

Pour ne pas afficher le nom, indiquer `display: 'none'` dans le yaml du chapitre.

```
authors:
    - forname:
      surname:
      orcidurl:
      display: 'none'
      presentation:
```

Le nom de l'auteur.rice apparaîtra néanmoins dans le [bloc de citation](chapitre4.html#afficher-ou-non-le-bloc-de-citation).

## Afficher ou non le bloc de citation

Le bloc de citation apparaît à la droite du titre de chapitre (cf. [plus haut](chapitre4.html)). Il comprend les informations permettant de citer le chapitre en cours de lecture.

![Exemple d'un bloc de citation](media/BlocDeCitationFIA.png)

Pour chaque page, il est possible d'afficher ou non ce bloc, en renseignant la clé `blockcitation` dans le yaml de chaque chapitre&nbsp;:

- `blockcitation: true` - le bloc apparaît,

- `blockcitation: false` - le bloc n'apparaît pas.


## Déclarer un ouvrage collectif

Dans le cas d'un livre collectif, avec des directeur·rice·s d'ouvrage et différent·e·s auteur·rice·s pour chaque chapitre, indiquer dans `livre.yaml`&nbsp;:

- `collective: true` (vs. `collective: false` pour un ouvrage non collectif)

- le ou les noms des directeur·rice·s d'ouvrages dans `authors`.

Le nom des auteur·rice·s de chaque chapitre devra être déclaré dans les yaml de chapitre (cf. [plus haut](chapitre4.html#afficher-ou-non-le-nom-de-lauteur.rice)).

Il sera alors précisé, [dans les blocs de citation](chapitre4.html#afficher-ou-non-le-bloc-de-citation), le nom de l'auteur·rice du chapitre ainsi que le ou les noms des directeur·rice·s de l'ouvrage collectif.


## Insérer une illustration

Pour ajouter une illustration dans le corps du texte&nbsp;:

- déposer le fichier dans `textes/media`,
- insérer à l'emplacement souhaité `![légende de l'image](lien vers l'image)`.

Par exemple&nbsp;:

```

![Illustration de livre ouvert](media/imagelivre.jpeg)

```

![Illustration de livre ouvert](media/imagelivre.jpeg)



## Styler une introduction de chapitre

Pour styler une introduction en début de chapitre (lettrine rouge, texte en gras[^2]), présenter le texte comme suit&nbsp;:

```

::: {.introchapitre}
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
:::

```


::: {.introchapitre}

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

:::


Cette fonctionnalité a initialement été pensée pour des ouvrages collectifs afin de signaler visuellement, au début de chaque chapitre, une mise en contexte rédigée par les directeur.rice.s de l'ouvrage.



## Contenus additionnels

Un contenu additionnel est un objet éditorial, qui prend la forme d'un encart[^1] et qui vient compléter la lecture. Il peut être placé&nbsp;:

- à la fin d'un chapitre (pour prolonger la réflexion après la lecture d'un chapitre),
- dans le corps du texte (pour illustrer un propos au cours de la lecture),
- dans une page `Contenus additionnels` à la fin de l'ouvrage (contenu additionnel attaché au livre dans sa globalité).

Chaque contenu additionnel est composé d'un ensemble d'informations --&nbsp;un identifiant, un [formulaire yaml](chapitre4.html#FormulaireYaml) (métadonnées) et éventuellement un texte en markdown&nbsp;-- qui doivent être déposées dans un fichier `additionnels.md`.


### Types de contenus additionnels

Il existe actuellement 4 types de contenus additionnels&nbsp;: `article`, `image`, `video`, `pageWeb`.

Le type est déclaré dans le formulaire yaml du contenu additionnel et correspond à un modèle d'affichage préalablement paramétré.

Ci-dessous un exemple de chacun des types&nbsp;:

!contenuadd(./ContenuAddTypeArticle)



!contenuadd(./ContenuAddTypeImage)



!contenuadd(./ContenuAddTypeVideo)



!contenuadd(./ContenuAddTypePageWeb)


### Ajouter un contenu additionnel dans un chapitre X

1. Créer un fichier `additionnels.md` dans le sous dossier du chapitre X. Exemple&nbsp;:

```
_textes
  |_ chapitreX
    |_ additionnels.md
    |_ chapitreX.bib
    |_ chapitreX.md
    |_ chapitreX.yaml
```

2. Remplir le [formulaire yaml]{#FormulaireYaml} du contenu dans `chapitreX/additionnels.md`

```
## identifiantUniqueDuContenuAdditionnel

---
title: >-
   ici le titre
credits: >-
   ici les crédits
keywords: ici,les,mots,cles
lang: fr (ou en, it...)
type: video ou pageWeb ou image ou article (le type correspond à un modèle d'affichage du contenu additionnel préalablement paramétré)
link: url
link-archive: url archivée
embed: code embed
zotero: clé bibtex
date: XXXX-XX-XX (du contenu)
date-publication: XXXX-XX-XX (sur la plateforme)
source: auteur ou éditeur
priority: highpriority (encart ouvert par défaut) ou lowpriority (encart fermé par défaut)
position: main
---

Texte en markdown (facultatif).

```

Certaines clés, non applicables selon les cas, peuvent rester vides.

3. Ajouter l'identifiant du contenu (`identifiantUniqueDuContenuAdditionnel`) à l'emplacement souhaité dans `chapitreX.md`, sous la forme suivante&nbsp;:

```
!contenuadd(./identifiantUniqueDuContenuAdditionnel)
```

À noter&nbsp;: l'identifiant du contenu additionnel doit être unique et ne doit pas comporter d'espace ou d'accent.


!contenuadd(./ExempleContenuAddOuvert)

!contenuadd(./ExempleContenuAddFerme)



## Balisage infra-textuel

Le balisage infra-textuel consiste à identifier tout au long du texte des termes sélectionnés, [appartenant à des "familles" ou catégories précédemment définies](chapitre3.html#definir-lindex), puis à les associer à des autorités, des liens (internes ou externes), des références bibliographiques, des définitions...

C'est à partir de ces termes que seront construits les index, mais aussi, selon les besoins, d'autres objets éditoriaux&nbsp;: glossaire, visualisation, cartographie...

Les termes balisés enrichissent la lecture puisqu'ils sont notifiés dans le corps du texte par le signe [+] qui permet d'ouvrir un volet donnant accès à des informations et des liens complémentaires.

!contenuadd(./ExempleBalisageIndex)


### Modèle de la balise

`[terme]{.balise idsp="terme complet" idautorité="lien vers l'autorité"}`

- la balise (`.balise`)&nbsp;: détermine à quelle «&nbsp;famille&nbsp;» appartient le terme balisé. Cette famille doit être déclarée dans le fichier de configuration `book.toml`[^3]. Elle ne doit pas comprendre d'espace ni d'accent.
- l'identifiant (`idsp`)&nbsp;: terme balisé «&nbsp;normé&nbsp;» et complet tel qu'il apparaîtra dans l'index final.
- l'autorité (`idautorité`)&nbsp;: url qui renvoie vers une autorité liée au terme balisé. Elle peut être, selon les paramètres par défaut, de trois types. Elle n'est pas obligatoire (si pas d'autorité, ne pas la mentionner).
    - `idorcid`&nbsp;: url vers un profil [ORCID](https://orcid.org/)
        - ex&nbsp;: [https://orcid.org/0000-0003-1599-221X](https://orcid.org/0000-0003-1599-221X)
    - `idwiki`&nbsp;: url vers une page [wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page)
        - ex&nbsp;: [https://www.wikidata.org/wiki/Q859](https://www.wikidata.org/wiki/Q859)
    - `idbnf`&nbsp;: url vers les notices d'autorité de la [BnF](https://catalogue.bnf.fr/recherche-autorite.do?pageRech=rat)
        - ex&nbsp;: [https://catalogue.bnf.fr/ark:/12148/cb120414160](https://catalogue.bnf.fr/ark:/12148/cb120414160)


### Clés de balise

Cette balise peut être complétée par les clés suivantes&nbsp;:    

- une clé bibtex (`idbib`) pour ajouter une référence bibliographique. Cette référence doit être présente dans le fichier `bibliographie.bib`.   

`[terme]{.balise idsp="terme complet" idautorité="lien vers l'autorité" idbib="@clebibtex"}`   

- un lien externe (`idreference`)  

`[terme]{.balise idsp="terme complet" idautorité="lien vers l'autorité" idreference="url"}`   

- un lien interne (`idglossaire`) (par exemple&nbsp;: vers un glossaire)   

`[terme]{.balise idsp="terme complet" idautorité="lien vers l'autorité" idglossaire="url"}`   


   Quand le terme balisé est déjà associé à un lien hypertexte, c'est l'ensemble `[terme](url)` qu'on met entre `[ ]`&nbsp;:

`[[terme](url)]{.balise idsp="terme complet" idautorité="lien vers l'autorité"}`


### Balises existantes

Sont listées ci-dessous les balises existantes, soit celles déjà utilisées dans les précédents ouvrages publiés avec le Pressoir&nbsp;:

- personnalités (`.personnalite`)

!contenuadd(./BalisePersonnalite)

- organismes (`.organisme`) (cf. [*Exigeons de meilleures bibliothèques*](http://ateliers.sens-public.org/exigeons-de-meilleures-bibliotheques/index.html))
- lieux (`.lieu`) (ex&nbsp;: villes, pays, quartiers... Cette balise peut être associée à une autorité Wikidata ou à des coordonnées géographiques.)
- sites internet ou plateformes numériques (`.site`) (cf. liste des plateformes citées dans [*Exigeons de meilleures bibliothèques*](http://ateliers.sens-public.org/exigeons-de-meilleures-bibliotheques/index.html))
- concepts (`.concept`) (cf. [*Lire Nietzsche à coups de sacoche*](http://ateliers.sens-public.org/lire-nietzsche-a-coups-de-sacoche/index.html))
- ouvrages (`.ouvrage`) (ex&nbsp;: tous les ouvrages de Nietzsche dans [*Lire Nietzsche à coups de sacoche*](http://ateliers.sens-public.org/lire-nietzsche-a-coups-de-sacoche/index.html))
- concepts créés (`.conceptCR`) (ex&nbsp;: tous les concepts créés par le groupe d'auteur.rice.s [FIA](http://ateliers.sens-public.org/fabrique-de-l-interaction-parmi-les-ecrans/index.html))
- concepts existants (`.conceptEX`) (cf. [FIA](http://ateliers.sens-public.org/fabrique-de-l-interaction-parmi-les-ecrans/index.html))
- dispositifs (`.dispositif`) (cf. [FIA](http://ateliers.sens-public.org/fabrique-de-l-interaction-parmi-les-ecrans/index.html))
- chaines YouTube (`.chaine`) (cf. [*Qu'est-ce que la littéraTube ?*](http://ateliers.sens-public.org/qu-est-ce-que-la-litteratube/index.html))

!contenuadd(./BaliseChaine)


Chaque balise est associée à un pictogramme présent dans le pavé informatif qui se déploie en cliquant sur le [+]. Lors de la création d'une nouvelle balise, il faut également penser à lui associer un nouveau pictogramme[^4].
<!-- ou et comment est-ce possible de faire ça pour une éditrice lambda ?-->


### Personnaliser

Il est possible de changer les intitulés des boutons qui apparaissent dans le pavé informatif de la balise en allant dans `book.toml`&nbsp;:

- `button-label` définit le texte visible sur le bouton
- `button-title` correspond au texte qui apparaît dans l'infobulle au survol du bouton


```
[glossaire]
button-label = "Voir sur l&rsquo;observatoire"
button-title = "Consulter la fiche sur le site de l&rsquo;observatoire"
```


## Index


Pour qu'un index soit généré à partir des termes balisés tout au long du texte, il est nécessaire de suivre les étapes suivantes&nbsp;:

- [déclarer des balises dans `book.toml`](chapitre3.html#definir-lindex),
- [baliser des termes dans le corps du texte](chapitre4.html#balisage-infra-textuel),
- dans un dossier index-np (`textes/index-np`), créer un fichier `index-np.md` et y indiquer la formule suivante&nbsp;:

```
<div>%INDEX%</div>
```

Référencer ensuite ce chapitre dans la `toc` du fichier `livre.yaml`.


## Recherche

Pour qu'une recherche soit rendue possible à partir des textes, il est nécessaire de suivre les étapes suivantes&nbsp;:

- dans un dossier recherche (`textes/recherche`), créer un fichier `recherche.md` et y indiquer la formule suivante&nbsp;:

```
<div>%SEARCH%</div>
```

Référencer ensuite ce chapitre dans la `toc` du fichier `livre.yaml`.

## Hypothes.is

Hypothes.is est un outil d'annotation implanté par défaut sur les ouvrages publiés avec le Pressoir. Il permet à toute personne ayant préalablement créé un compte sur la plateforme [Hypothes.is](https://web.hypothes.is/) de surligner et de commenter le texte, de manière privée --&nbsp;en créant un groupe privé&nbsp;-- ou publiquement (visible par tous). Il apparaît sous la forme de trois pictogrammes, en haut à droite de la fenêtre, sur les pages html produites par le Pressoir.

![Pictogrammes de l'outil d'annotation Hypothes.is](media/PictoHypothesis.png)


En cliquant sur le **<** (premier pictogramme), un panneau se déploie sur le côté droit de la fenêtre qui laisse apparaître les commentaires publics des précédent·e·s lecteurs et lectrices.





[^1]: Cf. [exemple 1](chapitre1.html#pre-requis-techniques) et [exemple 2](chapitre1.html#generer-la-documentation).

[^2]: [Voir exemple ci-dessus](chapitre4.html#styler-une-introduction-de-chapitre).

[^3]: Cf. [«Définir l'index»](chapitre3.html#definir-lindex) dans le chapitre précédent.

[^4]: Cf. [«Définir l'index»](chapitre3.html#definir-lindex) dans le chapitre précédent.

[^5]: [Voir plus bas la section «Chapitres additionnels»](chapitre4.html#contenus-additionnels).

[^6]: [Voir la section «Bibtex» dans «Créer un livre» pour en savoir plus sur la gestion de la bibliographie](chapitre2.html#bibtex).
