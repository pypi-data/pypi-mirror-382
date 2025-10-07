import json
import re

from jinja2 import Environment as Env
from jinja2 import FileSystemLoader
from jinja2.filters import do_striptags

from . import ROOT_DIR

environment = Env(loader=FileSystemLoader(str(ROOT_DIR / "templates")))


RE_CONTENUS_ADD = re.compile(r"!contenuadd(.*)")


def generate_search(search_index, book):
    template = environment.get_template("recherche.html")
    return template.render(search_index=search_index, book=book)


def write_search(output, content):
    index_html = output.read_text()
    index_html = index_html.replace("%SEARCH%", content)
    output.write_text(index_html)


def clean_html(html_content):
    html_content = re.sub(RE_CONTENUS_ADD, "", html_content)
    return (
        do_striptags(html_content)
        .replace("'", " ")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_search_page(repository_path, target_path, book, chapters):
    """Generate the search page and related index."""
    print(f"Initializing search for {repository_path}")
    search_index = []
    for chapter in chapters:
        if chapter.id not in ["index-np", "recherche"]:
            search_index.append(
                {
                    "book_title": book.title,
                    "book_url": book.url,
                    "book_coverurl": book.coverurl,
                    "title": chapter.title,
                    "url": chapter.url_relative,
                    "type": "chapitre",
                    "content": clean_html(chapter.html),
                }
            )
            for additional_content in chapter.additional_contents:
                search_index.append(
                    {
                        "book_title": book.title,
                        "book_url": book.url,
                        "book_coverurl": book.coverurl,
                        "title": additional_content.title,
                        "url": f"{chapter.url_relative}#{additional_content.id}",
                        "type": "contenu additionnel",
                        "content": clean_html(additional_content.html),
                    }
                )
    search_json = json.dumps(search_index, indent=2)
    (target_path / "recherche.json").write_text(search_json)
    search_content = generate_search(search_json, book)
    search_file = target_path / "recherche.html"
    if search_file.exists():
        write_search(search_file, search_content)
