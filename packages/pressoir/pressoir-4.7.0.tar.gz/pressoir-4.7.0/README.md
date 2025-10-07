# Pressoir

Documentation complète : https://pressoir.org/

## Utilisation rapide

1. Installer uv : https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
2. Se placer dans le dossier contenant les `textes`
3. Construire le livre : `uv run --with pressoir pressoir build serve`
4. Se rendre sur http://127.0.0.1:8000 pour visualiser le livre

Optionnellement, générer un PDF du livre :

5. Lancer : `uv run --with pressoir pressoir export`
6. Récupérer le PDF dans `public/book.pdf`

### À partir d’un corpus Stylo

1. Installer uv : https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
2. Se placer dans un nouveau dossier
3. Récupérer les textes : `uv run --with pressoir pressoir stylo <corpus-id>`
4. Construire le livre : `uv run --with pressoir pressoir build serve`
5. Se rendre sur http://127.0.0.1:8000 pour visualiser le livre


## Installation

Pré-requis : Python3.8+

Installer et activer un environnement virtuel :

    $ python3 -m venv venv
    $ source venv/bin/activate

Installer les dépendances :

    $ make install

## Initialiser un livre

Par exemple :

    $ pressoir init --repository-path=../fia --collection sp

ou

    $ pressoir init --repository-path=../12-editionscritiques --collection pum

Note : si la destination n’existe pas ou n’a pas de dossier `textes`,
une coquille complète du livre est créée.

Par exemple :

    $ mkdir livre-test
    $ cd livre-test
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install pressoir
    $ pressoir init --collection=sp

## Construire un livre

    $ pressoir build --repository-path=../fia-en

Avec `../fia-en` qui est le chemin vers le dépôt du livre.

En bonus, il est possible de passer un chapitre particulier pour ne reconstruire que lui :

    $ pressoir build --repository-path=../fia-en --chapter=chapter1

Si vous êtes en local / développement, il faut passer l’option `--local` 
pour que les liens de parcours du livre fonctionnent.


## Servir un livre

    $ pressoir serve --repository-path=../fia-en

Avec `../fia-en` qui est le chemin vers le dépôt du livre qui a été construit.


## Générer les md+tex+pdf d’un livre

Expérimental : il est possible avec la commande `pressoir export` de générer des fichiers markdown, tex et pdf à partir des sources. Ils vont être créés dans `public/book.{md|tex|pdf}`.

Il est nécessaire d’avoir (xe)latex pour effectuer cette génération.


## Help

### Commands

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir [-h]  ...

optional arguments:
  -h, --help  Show this help message and exit

Available commands:
  
    version   Return the current version of pressoir.
    init      Initialize a new book to `repository_path` or current directory.
    docs      Generate documentation with pressoir itself. #SoMeta
    build     Build a book from `repository_path` or current directory.
    export    Generate a single md+tex+pdf file from `repository_path` or
              current directory.
    serve     Serve an HTML book from `repository_path`/public or current
              directory/public.
    stylo     Initialize a new book to current directory from Stylo.

```
<!-- [[[end]]] -->

### Command: `init`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir init --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir init [-h] [--repository-path REPOSITORY_PATH]
                     [--collection {pum,sp,blank}]

optional arguments:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --collection {pum,sp,blank}, -c {pum,sp,blank}
                        Name of the collection (default: blank).

```
<!-- [[[end]]] -->


### Command: `docs`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir docs --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir docs [-h] [--target-path TARGET_PATH]

optional arguments:
  -h, --help            show this help message and exit
  --target-path TARGET_PATH

```
<!-- [[[end]]] -->


### Command: `build`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir build --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir build [-h] [--repository-path REPOSITORY_PATH]
                      [--csl-path CSL_PATH] [--target-path TARGET_PATH]
                      [--templates-folder TEMPLATES_FOLDER]
                      [--chapter CHAPTER] [--keep-statics] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --csl-path CSL_PATH   Path to .csl file (default: Pandoc’s default).
  --target-path TARGET_PATH
                        Where the book will be built (default:
                        `repository_path`/public).
  --templates-folder TEMPLATES_FOLDER
                        Folder with header.html/footer.html for before/after
                        inclusion.
  --chapter CHAPTER, -c CHAPTER
                        Specify a given chapter id (e.g. `chapter1`).
  --keep-statics        Do not override the statics with regular ones
                        (default: False).
  --verbose, -v         Display more informations during the build (default:
                        False).

```
<!-- [[[end]]] -->


### Command: `export`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir export --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir export [-h] [--repository-path REPOSITORY_PATH]
                       [--template-path TEMPLATE_PATH] [--csl-path CSL_PATH]
                       [--target-path TARGET_PATH] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Path to book’s sources (default: current).
  --template-path TEMPLATE_PATH
                        Path to .tex template (default: Pandoc’s default).
  --csl-path CSL_PATH   Path to .csl file (default: Pandoc’s default).
  --target-path TARGET_PATH
                        Where the book will be built (default:
                        `repository_path`/public).
  --verbose, -v         Display a lot of informations, useful for debugging.

```
<!-- [[[end]]] -->


### Command: `serve`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir serve --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir serve [-h] [--repository-path REPOSITORY_PATH] [--port PORT]

optional arguments:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --port PORT, -p PORT  Port to serve the book from (default=8000)

```
<!-- [[[end]]] -->

### Command: `stylo`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir stylo --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir stylo [-h] [--stylo-instance STYLO_INSTANCE]
                      [--stylo-export STYLO_EXPORT] [--from-scratch]
                      [--keep-metadata]
                      stylo_id

positional arguments:
  stylo_id              Corpus id from Stylo.

optional arguments:
  -h, --help            show this help message and exit
  --stylo-instance STYLO_INSTANCE
                        Instance of Stylo (default: stylo.huma-num.fr).
  --stylo-export STYLO_EXPORT
                        Stylo export URL (default: https://export.stylo.huma-
                        num.fr).
  --from-scratch        Do not ask to override local files (default: False).
  --keep-metadata       Do not override the `livre.yaml` metadata file
                        (default: False).

```
<!-- [[[end]]] -->
