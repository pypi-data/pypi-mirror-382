<!--
Questions / À faire :

- Valider le texte (notamment principes techniques)
- Ajouter des noms dans l'équipe ? Les classer par ordre alpha ?
- Ajouter autres contributeurs dans les financeurs ?

-->

::: {.introchapitre}
Pour en savoir plus sur les fondements, les objectifs et les protagonistes du Pressoir[^3].
:::

## Intention

Le Pressoir est un générateur de sites statiques conçu pour la création de livres enrichis en html. Pensé en priorité par et pour des chercheur·se·s en sciences humaines et sociales, il permet de publier des textes riches en données et en informations comprenant, notamment, des métadonnées détaillées, des bibliographies structurées, des notes de bas de page, un [balisage infra-textuel](chapitre3.html#balisage-infra-textuel) (permettant d'identifier des termes sélectionnés, de les relier à des autorités et de créer des objets éditoriaux&nbsp;: index, glossaire, cartographie...), des [contenus additionnels](chapitre3.html#contenus-additionnels) (illustrations, vidéos, compléments textuels...), des [index automatiques](chapitre3.html#index), un outil d'annotation (avec [Hypothes.is](https://web.hypothes.is/))...

En s'appuyant sur une chaîne de publication modulaire, ce générateur s'adapte aux besoins comme aux contraintes de l'édition numérique et peut être utilisé pour produire des livres enrichis, des supports de cours, de la documentation et tous types de publications numériques.

Voir les exemples d'usages suivants&nbsp;:

- les ouvrages publiés par [Les Ateliers de \[sens-public\]](https://ateliers.sens-public.org/),
- la collection [«&nbsp;Parcours Numériques&nbsp;»](http://parcoursnumeriques-pum.ca/) des Presses de l'Université de Montréal,
- [cette documentation](https://pressoir.org/).

Les références complètes de ces ouvrages se trouvent dans la [Bibliographie](bibliographie.html) disponible à la fin de cette documentation. <!-- Ajouter les liens vers les ouvrages ? -->

Initié par la [Chaire de recherche du Canada sur les écritures numériques](https://www.ecrituresnumeriques.ca/fr), le Pressoir est basé sur des outils libres et ouverts.
Le code est disponible en *open source* sous licence GPLv3 [sur un dépôt](https://gitlab.huma-num.fr/ecrinum/pressoir/) de l'instance [GitLab d'Huma-Num]{#ancreGitLab}.



## Principes techniques

Les choix techniques et éditoriaux ont été établis selon cinq principes généraux&nbsp;:

- la granularité des contenus et la structuration fine des données,
- la modularité de la chaîne éditoriale et des différents formats,
- le _low-tech_ appliqué aux formats et aux logiciels, comme garantie de soutenabilité et de pérennité de la chaîne et des contenus produits,
- la pérennité des données et de leur accessibilité,
- le logiciel libre, l'ouverture des sources et l'accès ouvert.

Suivant ces principes, les textes, les métadonnées et les références bibliographiques sont édités respectivement dans les formats _markdown_, _yaml_ et _bibtex_, à partir desquels le Pressoir produit des fichiers html statiques. Les ouvrages peuvent donc être simplement déposés sur un serveur, ou déployés via une forge logicielle.

Par défaut, le Pressoir met en page le corps de texte selon le style [Tufte](https://edwardtufte.github.io/tufte-css/), avec la police de caractère *Jannon* de Storm Type Foundry.


## Historique


À l'origine du projet, en 2018, le script de production était écrit en _bash_, et mobilisait les logiciels et langages suivants&nbsp;: _Pandoc_ (génération des contenus en html), _XSLT_ (enrichissement des html), _BaseX_ et _XQuery_ (production des index). Il a par la suite été implémenté dans un script Python destiné à l'usage interne des deux collections impliquées dans son développement&nbsp;: [Les Ateliers de \[sens-public\]](https://ateliers.sens-public.org/) et [«&nbsp;Parcours Numériques&nbsp;»](http://parcoursnumeriques-pum.ca/) (pour les Presses de l'Université de Montréal). Courant 2024, il a finalement été distribué comme paquet Python accessible à tou·te·s et utilisable au-delà des collections pour lequel il avait été originellement pensé[^1].


Pour en apprendre davantage sur l'histoire du Pressoir, consulter l'article (en anglais) [*Exploring New (Digital) Publishing Practices with Le Pressoir*](doi.org/10.54590/pop.2023.006) [@fauchie_exploring_2023].


## Équipe

Cet outil a été réalisé dans le cadre de la [Chaire de recherche du Canada sur les écritures numériques](https://www.ecrituresnumeriques.ca/fr) et grâce aux énergies de [Marcello Vitali Rosati]{.personnalite idsp="Vitali Rosati, Marcello" idorcid="https://orcid.org/0000-0001-6424-3229"}, [Nicolas Sauret]{.personnalite idsp="Sauret, Nicolas" idorcid="https://orcid.org/0000-0001-7516-3427"}, [Servanne Monjour]{.personnalite idsp="Monjour, Servanne" idorcid="https://orcid.org/0000-0003-1067-2145"}, [David Larlet]{.personnalite idsp="Larlet, David" idorcid="https://orcid.org/0000-0003-4244-7276"}, [Antoine Fauchié]{.personnalite idsp="Fauchié, Antoine" idorcid="https://orcid.org/0000-0003-1757-496X"}, [Michael Sinatra]{.personnalite idsp="Sinatra, Michael" idorcid="https://orcid.org/0000-0001-8943-4937"}, [Margot Mellet]{.personnalite idsp="Mellet, Margot" idorcid="https://orcid.org/0000-0001-7167-2136"}, [Hélène Beauchef]{.personnalite idsp="Beauchef, Hélène"} et [Roch Delannay]{.personnalite idsp="Delannay, Roch" idorcid="https://orcid.org/0000-0002-3519-4365"}[^2].


## Financement

La conception et le développement du Pressoir ont été financés par la [Chaire de recherche du Canada sur les écritures numériques](https://www.ecrituresnumeriques.ca/fr).

Ont également contribué le [Laboratoire Paragraphe](https://www.univ-paris8.fr/UR-Laboratoire-Paragraphe) (Université Paris 8) et le [Centre de recherche interuniversitaire sur les humanités numériques (CRIHN)](https://www.crihn.org/).


## Support

Pour remonter un problème, utiliser [les issues Gitlab](https://gitlab.huma-num.fr/ecrinum/pressoir/-/issues) en français ou en anglais.

[^1]: [Accéder à l'historique des versions du paquet Python](https://pypi.org/project/pressoir/#history).

[^2]: Le pictogramme [+] indique ici l'utilisation d'une des fonctionnalités développées pour le Pressoir&nbsp;: le balisage infra-textuel qui permet d'identifier des termes sélectionnés (ici, des personnes) et de les associer, notamment, à des autorités (ici, l'identifiant unique [ORCID](https://orcid.org/)). Pour en savoir plus sur cette fonctionnalité, voir la section [«&nbsp;Balisage infra-textuel&nbsp;»](chapitre2.html#balisage-infra-textuel).

[^3]: Ici est utilisée une fonctionnalité afin de styler l'introduction. [En savoir plus](chapitre4.html#styler-une-introduction-de-chapitre).



## Références
