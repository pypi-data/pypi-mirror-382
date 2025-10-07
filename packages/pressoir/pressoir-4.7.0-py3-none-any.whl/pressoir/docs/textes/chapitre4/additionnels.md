
## ExempleContenuAddOuvert

---
title: >-
   Exemple de contenu additionnel fermé par défaut
credits: >-
      Le Pressoir
keywords: contenu additionnel, fermé
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: lowpriority
position: main
---

Ceci est un exemple de contenu additionnel fermé par défaut.



## ExempleContenuAddFerme

---
title: >-
   Exemple de contenu additionnel ouvert par défaut
credits: >-
   Le Pressoir
keywords: contenu additionnel, ouvert
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: highpriority
position: main
---

Ceci est un exemple de contenu additionnel ouvert par défaut.


## ContenuAddTypeArticle

---
title: >-
   Exemple de contenu additionnel `type: article`
credits: >-
   Le Pressoir
keywords: contenu additionnel, article
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: highpriority
position: main
---

Ce type est adapté pour un contenu texte, comme un paragraphe complémentaire, un exemple détaillé, un long extrait...

Il est possible d'insérer, au sein de ce texte, tableau, image, liens externes et internes...


## ContenuAddTypePageWeb

---
title: >-
   Exemple de contenu additionnel `type: pageWeb`
credits: >-
   Le Pressoir
keywords: contenu additionnel, page web
lang: fr
type: pageWeb
link: https://ateliers.sens-public.org/
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: highpriority
position: main
---

Le bouton <u>Source</u> ci-dessous mène au lien indiqué dans le formulaire yaml, dans `link:`.


## ContenuAddTypeVideo

---
title: >-
   Exemple de contenu additionnel `type: video`
credits: >-
   Le Pressoir
keywords: contenu additionnel, video
lang: fr
type: video
link: https://youtu.be/a7hk_26OXts?si=vAofOKTCMk2paOAH
link-archive:
embed: https://www.youtube.com/embed/a7hk_26OXts?si=vAofOKTCMk2paOAH
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: highpriority
position: main
---

Un texte peut être ajouté afin de donner des informations complémentaires sur la vidéo présentée.


## ContenuAddTypeImage

---
title: >-
   Exemple de contenu additionnel `type: image`
credits: >-
   Le Pressoir
keywords: contenu additionnel, image
lang: fr
type: image
link: ./media/imagelivre.jpeg
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: highpriority
position: main
---

Un texte peut être ajouté afin de donner des informations complémentaires sur l'image.

Le bouton <u>Source</u> ci-dessous permet de voir l'image en grand format.

## BalisePersonnalite

---
title: >-
   Zoom sur la balise `.personnalite`
credits: >-
   Le Pressoir
keywords: balise, personnalité
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: lowpriority
position: main
---

**Objectif**&nbsp;: baliser toutes les personnes citées dans le texte.


Modèle de base&nbsp;:

`[nom]{.personnalite idsp="Nom, Prénom" idorcid ou idwiki ou idbnf="url"}`

Modèle pour un nom associé à un lien hypertexte&nbsp;:

`[[nom](url)]{.personnalite idsp="Nom, Prénom" idorcid ou idwiki ou idbnf="url"}`

Modèle pour le nom d'une personnalité qui est également l'auteur d'une chaîne YouTube (utilisé pour le livre [*Qu'est-ce que la littéraTube&nbsp;?*](http://ateliers.sens-public.org/qu-est-ce-que-la-litteratube/index.html))&nbsp;:

`[nom]{.personnalite idsp="Nom, Prénom" idorcid ou idwiki ou idbnf="url" idyoutubetitre="nom de la chaine YouTube" idyoutubeurl="url de la chaine YouTube"}`

À savoir&nbsp;:

- La balise `.personnalite` ne prend pas d'accent.
- L'`idsp` est ici sur le modèle "Nom, Prénom", ainsi les personnalités apparaissent dans l'index classées par ordre alphabétique en fonction de leur nom de famille. Tout autre modèle peut être adopté selon les besoins.
- L'`idautorite` est à choisir selon sa pertinence&nbsp;: pour une chercheuse contemporaine, on privilégiera par exemple son profil ORCID s'il existe. Si une personnalité dispose d'un profil sur Wikidata et sur le catalogue de la BnF, on choisira la page la plus renseignée/riche.
- On ne peut pas baliser un nom qui est dans un titre/sous-titre (titres de niveau 2, 3... ou titre de contenu additionnel) ou dans une légende (d'une vidéo, d'une image, d'un tableau).

Si une même personne est citée deux fois (ou plus), elle doit être à chaque fois balisée de la même manière, avec toujours le même `idsp`.

Exemple avec `idorcid`&nbsp;:

> Le philosophe `[[Pierre Lévy](http://fr.wikipedia.org/wiki/Pierre_L%C3%A9vy_%28philosophe%29)]{.personnalite idsp="Lévy, Pierre" idorcid="https://orcid.org/0000-0003-1599-221X"}` a été le premier...

> comme le dit `[[Lévy](http://fr.wikipedia.org/wiki/Pierre_L%C3%A9vy_%28philosophe%29)]{.personnalite idsp="Lévy, Pierre" idorcid="https://orcid.org/0000-0003-1599-221X"}`, le virtuel c'est bien...

Il s'agit ci-dessus de la même personne donc même `idsp` pour les deux formulations.


Exemple avec `idwiki`&nbsp;:

> Selon ce mythe, tel que raconté par `[[Platon](https://fr.wikipedia.org/wiki/Platon)]{.personnalite idsp="Platon" idwiki="https://www.wikidata.org/wiki/Q859"}` dans le *Protagoras*...


Exemple avec `idbnf`&nbsp;:

> Ainsi, souligne `[[Bertrand Legendre](http://labsic.univ-paris13.fr/index.php/legendre-bertrand)]{.personnalite idsp="Legendre, Bertrand" idbnf="https://catalogue.bnf.fr/ark:/12148/cb120414160"}`,...


Exemple d'un auteur de chaîne YouTube&nbsp;:

`[François Bon]{.personnalite idsp="Bon, François" idbnf="https://catalogue.bnf.fr/ark:/12148/cb371987603" idyoutubetitre="françois bon | le tiers livre" idyoutubeurl="https://www.youtube.com/@fbon"}`


Exemple d'un auteur de chaîne YouTube non présent sur ORCID/BnF/Wikidata&nbsp;:

`[Anh Mat]{.personnalite idsp="Mat, Anh" idyoutubetitre="Anh Mat" idyoutubeurl="https://www.youtube.com/@AnhMat"}`


## BaliseChaine

---
title: >-
   Zoom sur la balise `.chaine`
credits: >-
   Le Pressoir
keywords: balise, chaine
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: lowpriority
position: main
---

**Objectif**&nbsp;: baliser toutes les chaînes YouTube citées dans le texte.


Modèle de base&nbsp;:

`[nom de la chaîne]{.chaine idsp="nom de la chaîne" idyoutubetitre="url"}`

Modèle pour un nom associé à un lien hypertexte&nbsp;:

`[[nom de la chaîne](url)]{.chaine idsp="nom de la chaîne" idyoutubetitre="url"}`


À savoir&nbsp;:

- La balise `.chaine` s'écrit sans accent circonflexe.
- L'`idsp` est sur le nom de la chaîne tel quel (ex&nbsp;: Anh Mat, Milène Tournier, Pierre Menard, Marie lit en pyjama...).
- Le nom de l'auteur et le nom de la chaîne sont parfois différents (ex&nbsp;: François Bon / françois bon | le tiers livre, Ahmed Slama / Altérature ou Gracia Bejjani / gracia bejjani) et parfois identiques (ex&nbsp;: Milène Tournier, Anh Mat...).
- Dans le cas où le nom de la chaîne est identique au nom de l'auteur, le contexte détermine la balise&nbsp;: balise personnalité s'il est cité en tant qu'auteur, balise chaine s'il s'agit de la chaîne.

Si une même chaîne est citée deux fois (ou plus), il faut la baliser à chaque fois, de la même manière (même `idsp`).

Cette balise est utilisée dans l'ouvrage [*Qu'est-ce que la littéraTube&nbsp;?*](http://ateliers.sens-public.org/qu-est-ce-que-la-litteratube/index.html) publié aux Ateliers de [sens public].

## ExempleBalisageIndex

---
title: >-
   Exemple de volet Index
credits: >-
   Le Pressoir
keywords: balisage interne, index
lang: fr
type: image
link: ./media/volet-index.png
link-archive:
embed:
zotero:
date: 2024-10-08
date-publication: 2024-10-31
source: auteur
priority: lowpriority
position: main
---

Dans cet extrait, Philippe Bootz a été balisé comme "personnalité". Le signe [+] ouvre un volet Index permettant d'accéder à l'index des personnalités (extrait de l'ouvrage [_Qu'est-ce que la littéraTube&nbsp;?_](https://ateliers.sens-public.org/qu-est-ce-que-la-litteratube/introduction.html#%C3%A9l%C3%A9ments-de-d%C3%A9finition)).
