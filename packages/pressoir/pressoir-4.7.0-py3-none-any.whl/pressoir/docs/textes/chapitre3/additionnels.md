## parametragePolices

---
title: >-
   Exemple de référencement des polices dans `fonts.css`
credits:
keywords: police, référence, paramètres, fonts, css
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-09-20
date-publication: 2024-09-20
source: auteur
priority: lowpriority
position: main

---

```
@font-face {
    font-family: 'Averia Serif Libre';
    src: url('./fonts/averiaseriflibre-light.woff2') format('woff2');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}
@font-face {
    font-family: 'Averia Libre';
    src: url('./fonts/averialibre-bold.woff2') format('woff2');
    font-weight: bold;
    font-style: normal;
    font-display: swap;
}
```

## parametrageCouleurs

---
title: >-
   Exemple de paramétrage des couleurs dans `book.toml`
credits:
keywords: couleurs, graphisme, paramètres, book.toml
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-09-20
date-publication: 2024-09-20
source: auteur
priority: lowpriority
position: main

---

```
[theme]
# header
header-background-color = ["#FFF1C3", "#3dac75"]
header-border-color = ["#B35F1F", "#000"]

# table of content
toc-border-color = ["#FFF1C3", "#EBF6F1"]
toc-border-active-color = ["#B35F1F", "#3dac75"]

# balloon
balloon-color = ["#B35F1F", "#3dac75"]
balloon-color-font = ["#fff", "#000"]

# target background
target-background  = ["#78350F", "#EBF6F1"]
target-color = ["#fff", "#000"]

# contenus additionnels
contenuadd-border-color = ["#B35F1F", "#3dac75"]
contenuadd-background = ["#FFF8E3", "#EBF6F1"]

# svg
chevron-bottom-svg = ["#111", "#fffff8"]

# footer
footer-background-color = ["#FFF1C3", "#3dac75"]
footer-border-color = ["#B35F1F", "#000"]
```

## parametrageIndex

---
title: >-
   Exemple de définition de l'index dans `book.toml`
credits:
keywords: index, balise, paramètres, book.toml
lang: fr
type: article
link:
link-archive:
embed:
zotero:
date: 2024-09-20
date-publication: 2024-09-20
source: auteur
priority: lowpriority
position: main

---

```
[indexes]
ids = [
  "personnalite",
  "glossaire",
]
names = [
  "Personnalités",
  "Lexique",
]
images = [
  "./svg/personnalite.svg",
  "./svg/glossaire.svg",
]
```


## ExemplePictoBalise

---
title: >-
   Exemple de pictogrammes pour les catégories d'index
credits:
keywords: pictogramme, index, catégorie, balise, paramètres, book.toml
lang: fr
type: image
link: ./media/ExemplePictogrammesBalise.png
link-archive:
embed:
zotero:
date: 2024-09-20
date-publication: 2024-09-20
source: auteur
priority: lowpriority
position: main

---
