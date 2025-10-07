#!/usr/bin/env python3
import html
import re
import tempfile
from collections import namedtuple

import pypandoc
import yaml
from progressist import ProgressBar

from .utils import get_template_path, strip_html_comments

AdditionalContent = namedtuple("AdditionalContent", "id, title, type, yaml, md, html")
SEPARATOR = "## "


def extract_additional_data(repository_path, chapter):
    additional_path = repository_path / "textes" / chapter.id / "additionnels.md"
    if not additional_path.exists():
        return False
    additional_data = additional_path.read_text()
    if not additional_data.strip() or SEPARATOR not in additional_data:
        return False
    return additional_data


def extract_additional_content(repository_path, chapter, additional_item):
    try:
        additional_id, yaml_content, md_content = additional_item.split("---", 2)
    except ValueError as error:
        print(f"    /!\\ Error in {chapter.id}/additionels.md (malformed file)")
        print(additional_item)
        print(error)
        return False

    additional_id = additional_id.strip()
    if additional_id.startswith(SEPARATOR):
        additional_id = strip_html_comments(additional_id[len(SEPARATOR) :]).strip()

    try:
        yaml_content_loaded = yaml.load(yaml_content, Loader=yaml.Loader)
    except yaml.scanner.ScannerError as error:
        print(f"    /!\\ Error in {chapter.id}/additionels.md (malformed file)")
        print(error)
        return False

    additional_title = yaml_content_loaded.get("title")
    additional_type = yaml_content_loaded.get("type")

    if additional_type is None:
        return False

    if additional_type.startswith("texte"):
        additional_type = "texte"
    elif additional_type in ["entretien", "situation", "tableau"]:
        additional_type = "article"
    template_path = get_template_path(repository_path, f"{additional_type}.html")
    with tempfile.NamedTemporaryFile() as metadata_file:
        yaml_content += "suppress-bibliography: true\n"
        metadata_file.write(yaml_content.encode("utf-8"))
        metadata_file.read()  # Required to be readable by Pandoc.
        bib_file = repository_path / "textes" / chapter.id / f"{chapter.id}.bib"
        extra_args = [
            "--ascii",
            "--citeproc",
            f"--template={template_path}",
            f"--metadata-file={metadata_file.name}",
            f"--variable=additional_id:{additional_id}",
        ]
        if bib_file.exists():
            extra_args.append(
                f"--bibliography={bib_file}",
            )
        html_content = pypandoc.convert_text(
            md_content, "html", format="md", extra_args=extra_args
        )
    return AdditionalContent(
        **{
            "id": additional_id,
            "title": additional_title,
            "type": additional_type,
            "yaml": yaml_content,
            "md": md_content,
            "html": html_content,
        }
    )


def extract_additional_contents(repository_path, chapter):
    additional_contents = []
    additional_data = extract_additional_data(repository_path, chapter)
    if not additional_data:
        return []
    additional_parts = additional_data.split(f"\n{SEPARATOR}")
    bar = ProgressBar(
        total=len(additional_parts), prefix="    Loading additional contents:"
    )
    for additional_item in bar.iter(additional_parts):
        if not additional_item:
            continue
        additional_content = extract_additional_content(
            repository_path, chapter, additional_item
        )
        if not additional_content:
            continue
        additional_contents.append(additional_content)
    return additional_contents


def include_additional_contents(repository_path, chapter, html_content):
    # Useful to be able to match the `contenuadd_pattern`, otherwise
    # escaped special chars will not match:
    # "EnvironnementNumérique" vs. "EnvironnementNum&#xE9;rique".
    pattern = r"!contenuadd\((.*?)\)"
    html_content = re.sub(
        pattern, lambda m: f"!contenuadd({html.unescape(m.group(1))})", html_content
    )
    chapter.additional_contents = (
        chapter.additional_contents if hasattr(chapter, "additional_contents") else []
    )
    for additional_content in extract_additional_contents(repository_path, chapter):
        contenuadd_pattern = f"!contenuadd(./{additional_content.id})"
        html_content = html_content.replace(
            f"<p>{contenuadd_pattern}</p>",
            f"<!-- From: {contenuadd_pattern} -->\n{additional_content.html}",
        )
        chapter.additional_contents.append(additional_content)
    return html_content
