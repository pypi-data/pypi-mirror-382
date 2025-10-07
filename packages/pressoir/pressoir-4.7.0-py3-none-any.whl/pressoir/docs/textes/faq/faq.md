<!--
mettre ici les points qui ne vont pas ailleurs
-->

::: {.introchapitre}
Réponses aux questions sur les pratiques éditoriales.
:::


## Comment styler une épigraphe&nbsp;?

::: {.epigraphe}
[Ceci]{#epigraphe} est un exemple d'épigraphe.
:::

Pour insérer une épigraphe dans le texte, utiliser la balise suivante&nbsp;:

```
::: {.epigraphe}
Ceci est un exemple d'épigraphe.
:::
```


## Comment insérer une citation&nbsp;?

Sauter une ligne et introduire le texte de la citation par un `>`.

Sauter à nouveau une ligne pour revenir au corps de texte.

Par exemple&nbsp;:

```
L’album de famille consulté par le narrateur n’est plus la trace du réel ni du passé, mais entérine la disparition des parents et la perte des souvenirs d’enfance :

> Sur la photo le père a l’attitude du père. Il est grand. Il a la tête nue, il tient son calot à la main. Sa capote descend très bas. Elle est serrée à la taille par l’un de ces ceinturons de gros cuir qui ressemblent aux sangles des vitres dans les wagons de troisième classe. […] Le père sourit. C’est un simple soldat. Il est en permission à Paris, c’est la fin de l’hiver au bois de Vincennes (Perec 1975, 42).

Curieusement en retrait, Perec se livre à un examen clinique de la figure du père [...] [@monjourMythologiesPostphotographiquesInvention2018].

```

Ce qui donnera&nbsp;:


L’album de famille consulté par le narrateur n’est plus la trace du réel ni du passé, mais entérine la disparition des parents et la perte des souvenirs d’enfance&nbsp;:

> Sur la photo le père a l’attitude du père. Il est grand. Il a la tête nue, il tient son calot à la main. Sa capote descend très bas. Elle est serrée à la taille par l’un de ces ceinturons de gros cuir qui ressemblent aux sangles des vitres dans les wagons de troisième classe. […] Le père sourit. C’est un simple soldat. Il est en permission à Paris, c’est la fin de l’hiver au bois de Vincennes (Perec 1975, 42).

Curieusement en retrait, Perec se livre à un examen clinique de la figure du père [...] [@monjourMythologiesPostphotographiquesInvention2018].


## Comment ajouter une note de bas de page&nbsp;?

Les notes de bas de page apparaissent sur la droite du texte, en regarde des appels de note correspondants.

L'appel de note doit être inséré dans le corps du texte avec la syntaxe suivante&nbsp;:

```
[^]
```

Le contenu de la note, qui peut être placé à la fin du texte, doit être déclaré sous cette forme&nbsp;:

```
[^]: Contenu de la note.
```

Il n'y a pas d'espace entre l'appel de note et les `:` et un numéro ou un mot doit être ajouté après le `^` --&nbsp;dans l'appel de note comme dans la déclaration de son contenu&nbsp;-- afin de pouvoir identifier chaque note&nbsp;:

- `[^1]` / `[^1]: Contenu de la note.`
- `[^note1]` / `[^note1]: Contenu de la note.`
- `[^perseus]` / `[^perseus]: Contenu de la note.`

Par exemple&nbsp;:

```
> En 1333, Francesco Pétrarque découvre à Liège le manuscrit du discours de Cicéron Pro Archia[^1] [@alessiEditionsCritiquesNumeriques2023].

[^1]: Lire le Pro archia de Cicéron sur la plateforme Perseus de la Tufts University.
```

> En 1333, Francesco Pétrarque découvre à Liège le manuscrit du discours de Cicéron Pro Archia[^1] [@alessiEditionsCritiquesNumeriques2023].

[^1]: Lire le Pro archia de Cicéron sur la plateforme Perseus de la Tufts University.


La numérotation est faite automatiquement lors de la production des html, selon l'ordre d'apparition des appels de note dans le corps du texte, peu importe le numéro ou l'information indiquée dans l'appel.

```
> Un dernier point&nbsp;: on a souvent insisté sur le fait que les Alexandrins ne faisaient que placer dans les marges du texte des signes discrets[^46] pour ne destiner leur commentaire qu’à un volume séparé[^callimaque].
>
> [...]
>
> Il ne faut pas oublier que près de mille cinq cents ans séparent le texte autographe de Sophocle du témoin le plus ancien qui nous permet d’en avoir connaissance[^note2] [@alessiEditionsCritiquesNumeriques2023].

[^46]: L’obèle pour signaler un texte inauthentique, la diple, la diple pointée, l’astérisque et l’antisigma. Voir Reynolds et Wilson (1991, 10‑11).

[^callimaque]: Voir cependant le cas du pap. Lille 76d de Callimaque (IIIe s.) (Reynolds et Wilson 1991, 245‑46), dans lequel texte et notes se succèdent.

[^note2]: Cet exemple est donné par Jean Irigoin (1997, 7).
```

> Un dernier point : on a souvent insisté sur le fait que les Alexandrins ne faisaient que placer dans les marges du texte des signes discrets[^6] pour ne destiner leur commentaire qu’à un volume séparé[^callimaque].
>
> [...]
>
> Il ne faut pas oublier que près de mille cinq cents ans séparent le texte autographe de Sophocle du témoin le plus ancien qui nous permet d’en avoir connaissance[^note2] [@alessiEditionsCritiquesNumeriques2023].

[^6]: L’obèle pour signaler un texte inauthentique, la diple, la diple pointée, l’astérisque et l’antisigma. Voir Reynolds et Wilson (1991, 10‑11).

[^callimaque]: Voir cependant le cas du pap. Lille 76d de Callimaque (IIIe s.) (Reynolds et Wilson 1991, 245‑46), dans lequel texte et notes se succèdent.

[^note2]: Cet exemple est donné par Jean Irigoin (1997, 7).


## Comment insérer une espace insécable&nbsp;?

Pour signifier une espace insécable (avant ou après un signe de ponctuation, des guillemets français, des tirets cadratins ou entre deux mots...), utiliser l'entité html suivante&nbsp;: `&amp;nbsp;`

```
Par exemple&amp;nbsp;: n'hésitez pas à mettre des espaces insécables&amp;nbsp;!

```

## Comment insérer un tableau&nbsp;?

La mise en forme des tableaux en markdown respecte les principes suivants&nbsp;:

- les colonnes sont définies par des `|`,
- les lignes sont définies par un saut de ligne,
- les informations renseignées dans la première ligne correspondent aux titres de colonne,
- dans la deuxième ligne pourra être spécifié le mode d'alignement du texte dans les cellules,
- les lignes suivantes comprennent les informations du tableau.


```
|Titre1|Titre2|Titre3|
|:--:|:--|--:|
|rond|automne|20|
|carré|hiver|63|
|rectangle|printemps|47|
```

Ce tableau apparaîtra de la manière suivante&nbsp;:

|Titre1|Titre2|Titre3|
|:--:|:--|--:|
|rond|automne|20|
|carré|hiver|63|
|rectangle|printemps|47|


Si besoin de fonctions ou de mises en forme particulières (fusionner des cellules, moduler les tailles…), il est possible de mettre le tableau en html. Il devra alors être encadré par la balise `<table>`.

```
<table>

</table>
```

Pour voir quelques exemples, se référer aux tableaux réalisés pour les ouvrages [_Pratiques de l'édition numérique_](http://www.parcoursnumeriques-pum.ca/1-pratiques/introduction.html) ou à [_Expérimenter les humanités numériques_](http://www.parcoursnumeriques-pum.ca/introduction-140) (collection [«&nbsp;Parcours Numériques&nbsp;»](http://www.parcoursnumeriques-pum.ca/) aux Presses de l'Université de Montréal).



## Comment insérer un lien externe&nbsp;?

Pour insérer un lien externe, soit un hyperlien vers une autre plateforme ou un site internet tiers, utiliser la syntaxe suivante&nbsp;: `[terme](url)`

Exemple&nbsp;:

```
- Voir la collection [«&nbsp;Parcours numériques&nbsp;»](http://parcoursnumeriques-pum.ca/).
```

- Voir la collection [«&nbsp;Parcours numériques&nbsp;»](http://parcoursnumeriques-pum.ca/).



## Comment insérer un lien interne&nbsp;?

Un lien interne est un hyperlien vers une page ou un passage précis à l'intérieur d'un même ouvrage.

### Vers un autre chapitre

Pour insérer un lien interne vers une autre page, un autre chapitre du même ouvrage, la syntaxe est la suivante&nbsp;: `[terme](idchapitre.html)`

Exemple&nbsp;:

```
- [mon lien vers le chapitre «&nbsp;Présentation générale&nbsp;»](introduction.html)

- [mon lien vers le chapitre «&nbsp;Prise en main&nbsp;»](chapitre1.html)
```

- [mon lien vers le chapitre «&nbsp;Présentation générale&nbsp;»](introduction.html)

- [mon lien vers le chapitre «&nbsp;Prise en main&nbsp;»](chapitre1.html)



### Vers une section ou sous-section

Pour insérer un lien vers une section ou une sous-section (titre de niveau 2, 3...), utiliser la syntaxe suivante&nbsp;: `[terme](idchapitre.html#titre-de-section)`

Le titre de section ou de sous-section est indiqué tout en minuscule. Les mots sont séparés par des tirets (-).


Exemple&nbsp;:

```
- [mon lien vers la section «&nbsp;Comment insérer une citation&nbsp;?&nbsp;» de ce chapitre](faq.html#comment-inserer-une-citation)

- [mon lien vers la section «&nbsp;Initialiser un livre&nbsp;»](chapitre1.html#initialiser-un-livre)

- [mon lien vers la sous-section «&nbsp;Types de contenus additionnels&nbsp;»](chapitre4.html#types-de-contenus-additionnels)
```

- [mon lien vers la section «&nbsp;Comment insérer une citation&nbsp;?&nbsp;» de ce chapitre](faq.html#comment-inserer-une-citation)

- [mon lien vers la section «&nbsp;Initialiser un livre&nbsp;»](chapitre1.html#initialiser-un-livre)

- [mon lien vers la sous-section «&nbsp;Types de contenus additionnels&nbsp;»](chapitre4.html#types-de-contenus-additionnels)


### Vers un contenu additionnel

Pour insérer un lien vers un contenu additionnel&nbsp;: `[monlien vers contenu additionnel](idchapitre.html#idContenuAdditionnel)`


Exemple&nbsp;:

```
- [mon lien vers le contenu additionnel «&nbsp;Exemple d’arborescence du dossier MonLivre&nbsp;»](chapitre2.html#structure-du-livre)

```

- [mon lien vers le contenu additionnel «&nbsp;Exemple d’arborescence du dossier MonLivre&nbsp;»](chapitre2.html#structure-du-livre)



### Vers une ancre

Pour insérer un lien vers une ancre, utiliser les syntaxes suivantes&nbsp;:

1. Pour insérer un lien renvoyant à une ancre au sein d'un même chapitre&nbsp;:

- `[terme]{#monancre}` sera appelé par `[monlien vers terme](#monancre)`

2. Pour insérer un lien renvoyant à une ancre placée dans un autre chapitre&nbsp;:

- `[terme]{#monancre}` écrit dans le Chapitre 2 sera appelé dans le Chapitre 6 par `[monlien vers terme](chapitre2.html#monancre)`


Exemple&nbsp;:

```
- [mon lien vers l'épigraphe en début de ce chapitre](#epigraphe)

- [mon lien vers la mention du GitLab d'Human-Num dans «&nbsp;Présentation générale&nbsp;»](introduction.html#ancreGitLab)


```

- [mon lien vers l'épigraphe en début de ce chapitre](#epigraphe)

- [mon lien vers la mention du GitLab d'Human-Num dans «&nbsp;Présentation générale&nbsp;»](introduction.html#ancreGitLab)

## Comment générer un livre automatiquement avec l’intégration continue de Gitlab&nbsp;?

Vous pouvez ajouter le fichier `.gitlab-ci.yaml` suivant&nbsp;:

```yaml
image: ubuntu:24.04

variables:
  UV_CACHE_DIR: "$CI_PROJECT_DIR/.uv-cache"
  APT_DIR: "$CI_PROJECT_DIR/.apt"
  APT_STATE_LISTS: "$CI_PROJECT_DIR/.apt/lists"
  APT_CACHE_ARCHIVES: "$CI_PROJECT_DIR/.apt/archives"

cache:
  - key:
      files:
        - uv.lock
    paths:
      - $UV_CACHE_DIR
  - paths:
    - .apt/

before_script:
  # Install dependencies and create associated cache dirs
  - mkdir -p "${APT_STATE_LISTS}/partial"
  - mkdir -p "${APT_CACHE_ARCHIVES}/partial"
  - apt update -qy
  - apt install -y apt-utils
  - apt install -y curl python3
  - apt install -y locales locales-all
  - apt install -y pandoc

pages:
  stage: deploy
  script:
    # Optionnal: get feedback from current environment
    - ls -al
    - pwd
    - python3 --version
    # Install uv, see https://docs.astral.sh/uv/#getting-started
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    # Put uv in the path
    - source $HOME/.local/bin/env
    # Check the available version of Python
    - uv python list
    # Display the version of the Pressoir installed
    - uv run --with pressoir pressoir version
    # Build the book with dedicated target path (required)
    - uv run --with pressoir pressoir build --target-path=/data/runner/builds/${CI_PROJECT_NAMESPACE}/${CI_PROJECT_NAME}/public
    # Link to the generated book
    - echo "Book available at ${CI_PAGES_URL}"
    # See https://docs.astral.sh/uv/guides/integration/gitlab/#caching
    - uv cache prune --ci
  artifacts:
    paths:
      - public
  rules:
    # Only launch the CI if we are on the default branch (`main`)
    - if: $CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH
```



## Références
