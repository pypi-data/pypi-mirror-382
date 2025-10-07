import contextlib
import os
import shutil
import socket
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer, test
from pathlib import Path
from typing import Optional

import httpx
import yaml
from minicli import cli, run

from . import ROOT_DIR, VERSION
from .corpus import convert_stylo_articles, generate_book_metadata
from .generator import (
    generate_chapters,
    generate_homepage,
    generate_markdown,
    generate_pdf,
)
from .indexes import generate_indexes
from .models import configure_book
from .search import generate_search_page
from .statics import bundle_statics, sync_media, sync_statics


@cli
def version():
    """Return the current version of pressoir."""
    print(f"Pressoir version: {VERSION}")


@cli
@cli("collection", choices=["pum", "sp", "blank"])
def init(repository_path: Path = Path(), collection: str = "blank"):
    """Initialize a new book to `repository_path` or current directory.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :collection: Name of the collection (default: blank).
    """
    print(
        f"Initializing a new book: `{repository_path}` for `{collection}` collection."
    )

    if not (repository_path / "presssoir").exists():
        shutil.copytree(
            ROOT_DIR / "init" / collection / "pressoir",
            repository_path / "pressoir",
            dirs_exist_ok=True,
        )

    if "textes" not in os.listdir(repository_path):
        shutil.copytree(
            ROOT_DIR / "init" / collection / "textes",
            repository_path / "textes",
            dirs_exist_ok=True,
        )

    if "doc" not in os.listdir(repository_path) and "doc" in os.listdir(
        ROOT_DIR / "init" / collection
    ):
        shutil.copytree(
            ROOT_DIR / "init" / collection / "doc",
            repository_path / "doc",
            dirs_exist_ok=True,
        )


@cli
def docs(target_path: Optional[Path] = None):
    """Generate documentation with pressoir itself. #SoMeta"""
    if target_path is None:
        target_path = Path(os.getenv("PWD", "")) / "public"
    else:
        target_path = Path(target_path)
    print(f"Generating documentation in `{target_path.resolve()}`.")
    build(ROOT_DIR / "docs", target_path=target_path)  # , verbose=True)
    print("Don’t forget to generate the associated PDF file :)")
    print("pressoir export --repository-path=pressoir/docs")


@cli
def build(
    repository_path: Path = Path(),
    csl_path: Optional[Path] = None,
    target_path: Optional[Path] = None,
    templates_folder: Optional[Path] = None,
    chapter: str = "",
    keep_statics: bool = False,
    verbose: bool = False,
):
    """Build a book from `repository_path` or current directory.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :csl_path: Path to .csl file (default: Pandoc’s default).
    :target_path: Where the book will be built (default: `repository_path`/public).
    :templates_folder: Folder with header.html/footer.html for before/after inclusion.
    :chapter: Specify a given chapter id (e.g. `chapter1`).
    :keep_statics: Do not override the statics with regular ones (default: False).
    :verbose: Display more informations during the build (default: False).
    """
    if target_path is None:
        target_path = repository_path / "public"
    else:
        target_path = Path(target_path)
    if templates_folder is None:
        templates_folder = repository_path / "templates"
    else:
        templates_folder = Path(templates_folder).resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    print(
        f"Building a book from {repository_path.resolve()} to {target_path.resolve()}."
    )
    book = configure_book(repository_path / "textes" / "garde" / "livre.yaml")
    if not keep_statics:
        sync_media(repository_path, target_path, book)
        sync_statics(repository_path, target_path)
    css_filename, js_filename = bundle_statics(repository_path, target_path)
    if verbose:
        import pprint

        pprint.pprint(book)

    meta = {"css_filename": css_filename, "js_filename": js_filename}
    generate_homepage(repository_path, target_path, templates_folder, book, meta)
    chapters = generate_chapters(
        repository_path, csl_path, target_path, book, meta, chapter
    )
    generate_indexes(repository_path, target_path, book)
    generate_search_page(repository_path, target_path, book, chapters)


@cli
def export(
    repository_path: Path = Path(),
    template_path: Optional[Path] = None,
    csl_path: Optional[Path] = None,
    target_path: Optional[Path] = None,
    verbose: bool = False,
):
    """Generate a single md+tex+pdf file from `repository_path` or current directory.

    :repository_path: Path to book’s sources (default: current).
    :template_path: Path to .tex template (default: Pandoc’s default).
    :csl_path: Path to .csl file (default: Pandoc’s default).
    :target_path: Where the book will be built (default: `repository_path`/public).
    :verbose: Display a lot of informations, useful for debugging.
    """
    if target_path is None:
        target_path = repository_path / "public"
    else:
        target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)
    print(
        f"Generating file from {repository_path.resolve()} to {target_path.resolve()}."
    )
    book = configure_book(repository_path / "textes" / "garde" / "livre.yaml")
    if verbose:
        import pprint

        pprint.pprint(book)
    generate_markdown(repository_path, target_path, book)
    generate_pdf(repository_path, template_path, csl_path, target_path, book)


@cli
def serve(repository_path: Path = Path(), port: int = 8000):
    """Serve an HTML book from `repository_path`/public or current directory/public.

    :repository_path: Absolute or relative path to book’s sources (default: current).
    :port: Port to serve the book from (default=8000)
    """
    print(
        f"Serving HTML book from `{repository_path}/public` to http://127.0.0.1:{port}"
    )

    # From https://github.com/python/cpython/blob/main/Lib/http/server.py#L1307-L1326
    class DirectoryServer(ThreadingHTTPServer):
        def server_bind(self):
            # suppress exception when protocol is IPv4
            with contextlib.suppress(Exception):
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            return super().server_bind()

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(
                request, client_address, self, directory=str(repository_path / "public")
            )

    test(HandlerClass=SimpleHTTPRequestHandler, ServerClass=DirectoryServer, port=port)


@cli
def stylo(
    stylo_id: str,
    stylo_instance: str = "stylo.huma-num.fr",
    stylo_export: str = "https://export.stylo.huma-num.fr",
    from_scratch: bool = False,
    keep_metadata: bool = False,
):
    """Initialize a new book to current directory from Stylo.

    :stylo_id: Corpus id from Stylo.
    :stylo_instance: Instance of Stylo (default: stylo.huma-num.fr).
    :stylo_export: Stylo export URL (default: https://export.stylo.huma-num.fr).
    :from_scratch: Do not ask to override local files (default: False).
    :keep_metadata: Do not override the `livre.yaml` metadata file (default: False).
    """
    print(
        f"Initializing a new corpus: `{stylo_id}` from `{stylo_instance}` "
        f"through export service `{stylo_export}`."
    )

    if not (Path() / "presssoir").exists():
        print("Copying Pressoir-related files from `blank` init.")
        shutil.copytree(
            ROOT_DIR / "init" / "blank" / "pressoir",
            Path() / "pressoir",
            dirs_exist_ok=True,
        )

    textes_path = Path() / "textes"
    if not textes_path.exists():
        Path.mkdir(textes_path)
    else:
        if (
            from_scratch
            or input("Écraser les textes locaux avec ceux de Stylo ? (O / N) ") == "O"
        ):
            print("Erasing existing local textes…")
            shutil.rmtree(textes_path)
            Path.mkdir(textes_path)
        else:
            print("Keeping existing local textes. Nothing updated from Stylo.")
            return

    url = (
        f"{stylo_export}/generique/corpus/export/"
        f"{stylo_instance}/{stylo_id}/Extract-corpus/"
        "?with_toc=0&with_ascii=0&with_link_citations=0&with_nocite=0"
        "&version=&bibliography_style=chicagomodified&formats=originals"
    )
    zip_path = Path() / f"export-{stylo_id}.zip"
    print(f"Downloading data from {url} to {zip_path}")
    with Path.open(zip_path, "wb") as fd:
        with httpx.stream("GET", url, timeout=None) as r:
            for data in r.iter_bytes():
                fd.write(data)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(textes_path)
        print(f"Data downloaded and extracted to {textes_path}")
    except zipfile.BadZipFile:
        print(f"Unable to find corpus with id {stylo_id}!")
        return

    convert_stylo_articles(textes_path, pressoir_dirs=["garde", "media", "corpus"])

    Path.mkdir(textes_path / "garde", exist_ok=True)
    shutil.copy(
        ROOT_DIR / "init" / "blank" / "textes" / "garde" / "homepage.md",
        textes_path / "garde",
    )

    if keep_metadata:
        return

    print("Generating metadata for book")
    corpus_data = next(yaml.safe_load_all((textes_path / "corpus.yaml").read_text()))
    print(f"From corpus data: {corpus_data}")
    book_metadata = generate_book_metadata(textes_path, corpus_data)
    print(f"To pressoir data: {book_metadata}")
    book_yaml = yaml.dump(book_metadata)
    with Path.open(textes_path / "garde" / "livre.yaml", "w") as metadata_file:
        metadata_file.write(book_yaml)


def main():
    run()
