<!--insérer ci-dessous le texte en markdown de l'introduction-->

## I. Titre de section

::: {.epigraphe}
Je peux ajouter une épigraphe.
:::

**Ici je mets du gras**.

*Ici je mets de l'italique*.

J'insère des espaces fines insécables quand nécessaire, par exemple avant un signe de ponctuation double&nbsp;: comme ici&nbsp;!

### I.1. Titre de sous-section

Ici je vais faire une liste à puces&nbsp;:

- point 1
- point 2
- point 3

#### I.1.a. Titre de sous-sous-section

Je peux la faire aussi numérotée (le 1^er^ point va vous surprendre)&nbsp;:

1. point 1
2. point 2
3. point 3

#### I.1.b. Titre de sous-sous-section

Ici j'insère une citation&nbsp;:

> Nunc scelerisque viverra mauris in aliquam sem fringilla. Consectetur adipiscing elit duis tristique sollicitudin nibh sit amet commodo. Volutpat diam ut venenatis tellus in metus.

### I.2. Titre de sous-section

Maintenant je souhaite ajouter une note[^1], un [lien interne vers le chapitre 2](chapitre2.html) et un [lien externe pour en savoir plus sur la syntaxe Markdown](http://stylo-doc.ecrituresnumeriques.ca/fr/syntaxemarkdown/).

![Légende de l'image](./media/imagelivre.jpeg)

<!-- pour insérer une illustration directement dans le corps du texte-->



## II. Titre de section

Je peux insérer un lien interne vers une section de ce chapitre, [la section 4-a par exemple](introduction.html#introduction-ii-2-titre-de-sous-section-niveau-3b), ou vers une section d'un autre chapitre -- [la section 3a du chapitre 1](chapitre1.html#chapitre1-titre-niveau-3a).    
   Je peux aussi ajouter un lien interne vers [un passage en particulier](#mon-ancre) et un contenu additionnel ouvert ou fermé par défaut&nbsp;:

!contenuadd(./idCA1)


!contenuadd(./idCA2)


## II.1. Titre de sous-section

J'ajoute aussi une référence bibliographique [@lankesExigeonsMeilleuresBibliotheques2018a], une autre avec un numéro de page [@lankesExigeonsMeilleuresBibliotheques2018a, p.12], une autre sans le nom de l'auteur que je vais citer juste avant dans le texte&nbsp;: Lankes [-@lankesExigeonsMeilleuresBibliotheques2018a], puis deux références ensemble [@lankesExigeonsMeilleuresBibliotheques2018a ; @theriaultLireNietzscheCoups2022] et enfin dans une note[^2].

## II.2. Titre de sous-section

Pour avoir des sources pérennes, j'archive mes liens externes à l'aide de la WayBack machine et je l'intègre dans le texte sous cette forme&nbsp;: [texte cliquable](http://stylo-doc.ecrituresnumeriques.ca/fr/syntaxemarkdown/){link-archive="https://web.archive.org/web/20240120165525/http://stylo-doc.ecrituresnumeriques.ca/fr/syntaxemarkdown/"}.



[^1]: Enim tortor at auctor urna nunc id cursus.

[^2]: @monjourMythologiesPostphotographiquesInvention2018


## Contenus additionnels

<!-- si pas de CA, supprimer le titre de niveau 2 -->

!contenuadd(./idCA3)

!contenuadd(./idCA4)


## Références

<!-- C'est ici que s'afficheront les références bibliographiques du fichier introduction.bib dans le html. Si pas de références, supprimer le titre de niveau 2-->
