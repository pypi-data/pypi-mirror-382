import re
import shutil

import yaml
from slugify import slugify

from .utils import each_file_from, each_folder_from


def generate_book_metadata(textes_path, corpus_data):
    corpus_metadata = corpus_data.get("metadata") or {}
    articles_titles = [
        slugify(article["article"]["title"]) for article in corpus_data.get("articles")
    ]
    articles_authors = []
    for article in corpus_data.get("articles"):
        for yaml_file in each_file_from(
            textes_path / article["article"]["title"], pattern="*.yaml"
        ):
            article_data = next(yaml.safe_load_all(yaml_file.read_text()))
            articles_authors += article_data.get("authors", [])

    book_metadata = {
        "title": corpus_metadata.get("issue", {}).get("title", "Titre à définir"),
        "version": corpus_metadata.get("@version"),
        "lang": "fr",
        "date": "2025-01-28",
        "rights": (
            "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)"
        ),
        "url": "",
        "collective": False,
        "coverurl": "",
        "abstract_fr": "Résumé",
        "abstract_en": "Abstract",
        "keyword_fr": "",
        "keyword_en": "",
        "isbnprint": "",
        "isbnepub": "",
        "isbnpdf": "",
        "isbnnum": "",
        "publisher": "Pressoir éditions",
        "place": "Montréal",
        "authors": articles_authors,
        "toc": [{"id": article_title} for article_title in articles_titles],
    }
    return book_metadata


def rewrite_image_paths(md_file):
    print(f"Rewriting image paths from `images/` to `media/` in {md_file}")
    md_file.write_text(md_file.read_text().replace("images/", "media/"))


RE_ADD_CONTENTS = re.compile(
    r"(?s):{3}\s*{\s?\.contenuadd\s*#(?P<id>.*?)\s?}\n(?P<content>.*?)\n:{3}"
)


def extract_additional_contents(md_file):
    md_content = md_file.read_text()
    matcher = ":::"

    if matcher in md_content:
        additional_contents = ""
        additional_references = []
        for match in RE_ADD_CONTENTS.finditer(md_content):
            id_ = match.group("id").strip()
            content = match.group("content").strip()
            additional_contents += f"## {id_}\n\n{content}\n\n"
            additional_references.append([id_, match.span()])
        (md_file.parent / "additionnels.md").write_text(additional_contents)
        # Reverse is important to keep positions while iterating.
        for id_, span in reversed(additional_references):
            md_content = (
                md_content[: span[0]] + f"!contenuadd(./{id_})" + md_content[span[1] :]
            )
        md_file.write_text(md_content)


def convert_stylo_articles(textes_path, pressoir_dirs):
    for folder in each_folder_from(textes_path):
        if folder.name in pressoir_dirs:
            continue
        for subfolder in each_folder_from(folder):
            if subfolder.name == "images":
                print("Copying images from `images/` to `media/`")
                shutil.copytree(subfolder, textes_path / "media", dirs_exist_ok=True)
                for md_file in each_file_from(folder, pattern="*.md"):
                    rewrite_image_paths(md_file)
        for md_file in each_file_from(folder, pattern="*.md"):
            extract_additional_contents(md_file)

        target = folder.parent / "-".join(folder.name.split("-")[:-1])
        print(f"Renaming folder {folder} to {target}")
        folder.rename(target)
