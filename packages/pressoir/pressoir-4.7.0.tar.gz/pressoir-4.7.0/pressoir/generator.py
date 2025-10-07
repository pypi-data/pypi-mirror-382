import re
import tempfile

import pypandoc
import yaml
from dataclass_wizard.dumpers import asdict
from slugify import slugify

from .additionals import include_additional_contents
from .models import Part
from .sidenotes import convert_sidenotes, rewrite_global_sidenotes
from .utils import get_template_path, neighborhood

try:
    print(f"Pandoc version: {pypandoc.get_pandoc_version()}")
except OSError:
    pypandoc.download_pandoc()
    print(f"Pandoc version: {pypandoc.get_pandoc_version()}")

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

RE_CONTENUS_ADD = re.compile(r"\n\n!contenuadd(.*)")


def generate_chapters(repository_path, csl_path, target_path, book, meta, chapter_id):
    print("  Generating chapters:")
    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )

    indexes_ids = book_settings.get("indexes", {}).get("ids")
    meta["indexes"] = indexes_ids
    glossaire = book_settings.get("glossaire", {})
    meta["glossaire"] = {
        "button": {
            "label": glossaire.get("button-label", "Voir dans le glossaire"),
            "title": glossaire.get(
                "button-title", "Consulter la référence dans le glossaire de l’ouvrage"
            ),
        }
    }
    meta["nb_of_chapters"] = len(book.chapters)
    indexed_chapters = []

    for index, previous_chapter, current_chapter, next_chapter in neighborhood(
        book.chapters
    ):
        meta["index"] = index
        if not chapter_id or chapter_id == current_chapter.id:
            chapter = generate_chapter(
                repository_path,
                csl_path,
                target_path,
                book,
                current_chapter,
                previous_chapter,
                next_chapter,
                meta,
            )
            indexed_chapters.append(chapter)
    return indexed_chapters


def generate_chapter(
    repository_path,
    csl_path,
    target_path,
    book,
    current_chapter,
    previous_chapter,
    next_chapter,
    meta,
):
    print(
        f"    {current_chapter.id}: {current_chapter.title_h} "
        + f"({meta['index']}/{meta['nb_of_chapters']})"
    )
    dict_content = {
        "book": asdict(book),
        "chapter": asdict(current_chapter),
        "prev": (previous_chapter and asdict(previous_chapter)) or "",
        "next": (next_chapter and asdict(next_chapter)) or "",
        "meta": meta,
    }
    yaml_content = yaml.dump(dict_content)
    yaml_content += "nocite: '[@*]'\n"
    with tempfile.NamedTemporaryFile() as metadata_file:
        metadata_file.write(yaml_content.encode("utf-8"))
        metadata_file.read()  # Required to be readable by Pandoc.
        html_content = generate_html_content(
            repository_path, csl_path, book, current_chapter, metadata_file
        )
        # This is fragile and depends on templates.
        _, main = html_content.split("<main>", 1)
        content, _ = main.split("</main>", 1)
        current_chapter.html = content
    html_content = rewrite_global_sidenotes(html_content)
    html_content = include_additional_contents(
        repository_path, current_chapter, html_content
    )
    html_content = convert_sidenotes(html_content)
    (target_path / f"{current_chapter.id}.html").write_text(html_content)
    return current_chapter


def generate_html_content(
    repository_path, csl_path, book, current_chapter, metadata_file
):
    textes_path = repository_path / "textes"
    chapter_id = current_chapter.id
    md_content = (textes_path / chapter_id / f"{chapter_id}.md").read_text()
    bib_file = textes_path / chapter_id / f"{chapter_id}.bib"
    zotero_collection = current_chapter.zoteroCollection
    zotero_description = book.zoteroDescription
    extra_refs = ""
    if zotero_collection:
        extra_refs = f"""
<a href="{zotero_collection}" title="Collection Zotero du chapitre" class="zotero">
    <strong>{zotero_description}</strong>
</a>
        """
    md_content = md_content.replace(
        "## Références",
        f"""
<section>
<details class="references" open>
<summary id="references">Références</summary>

{extra_refs}

:::{{#refs}}
:::

</details>
</section>""",
    )

    template_path = get_template_path(repository_path, "chapitre.html")
    lang = current_chapter.lang or book.lang or "fr"
    extra_args = [
        "--ascii",
        "--citeproc",
        f"--template={template_path}",
        f"--metadata=lang:{lang}",
        f"--metadata=title:{current_chapter.title_f}",
        f"--metadata-file={metadata_file.name}",
    ]
    if bib_file.exists():
        extra_args.append(f"--bibliography={bib_file}")
    if csl_path is not None:
        extra_args.append(f"--csl={csl_path}")

    html_content = pypandoc.convert_text(
        md_content,
        "html",
        format="markdown+auto_identifiers+ascii_identifiers",
        extra_args=extra_args,
    )

    return html_content


def generate_homepage(repository_path, target_path, templates_folder, book, meta):
    print(f"Rendering {target_path}:")
    print("  Generating homepage")

    source = repository_path / "textes" / "garde" / "homepage.md"
    if not source.exists():
        print("    Homepage not generated (missing homepage.md file)")
        return
    dict_content = {
        "book": asdict(book),
        "meta": meta,
    }
    yaml_content = yaml.dump(dict_content)
    yaml_content += "nocite: '[@*]'\n"
    with tempfile.NamedTemporaryFile() as metadata_file:
        metadata_file.write(yaml_content.encode("utf-8"))
        metadata_file.read()  # Required to be readable by Pandoc.
        md_content = (repository_path / "textes" / "garde" / "homepage.md").read_text()
        template_path = get_template_path(repository_path, "homepage.html")
        extra_args = [
            "--ascii",
            "--citeproc",
            f"--template={template_path}",
            f"--metadata=title:{book.title_f}",
            f"--metadata=first_chapter_id:{dict_content['book']['chapters'][0]['id']}",
            f"--metadata-file={metadata_file.name}",
        ]

        template_header = templates_folder / "header.html"
        if template_header.exists():
            extra_args.append(f"--include-before-body={template_header}")
        template_footer = templates_folder / "footer.html"
        if template_footer.exists():
            extra_args.append(f"--include-after-body={template_footer}")

        # By default, pressoir assumes there are multipe authors.
        # Check whether there is more than one author, and pass an extra
        # variable as a cli argument to pandoc. A variable with no specified
        # value is automatically assigned to true. This exists to work around a
        # limitation in pandoc templates, where you cannot make complex
        # conditional statements, but only check for variable truthfullness.
        if len(dict_content["book"]["authors"]) == 1:
            extra_args.append("--variable=singleauthor")

        html_content = pypandoc.convert_text(
            md_content, "html", format="md", extra_args=extra_args
        )

    (target_path / "index.html").write_text(html_content)


def prepare_chapter_markdown(
    repository_path, filenames_to_slugs, chapter_or_part, within_part=False
):
    textes_path = repository_path / "textes"
    chapter_id = chapter_or_part.id

    if chapter_id in ["bibliography", "index-np", "recherche"]:
        return None, None

    # If the chapter is within a part we want to start at the second level
    # and pass on to subsequent titles the new hierarchy.
    chapter_title_level = "#"
    if within_part:
        chapter_title_level = "##"

    md_content = (textes_path / chapter_id / f"{chapter_id}.md").read_text()

    # Fix internal references.
    for filename, slug in filenames_to_slugs.items():
        # First we consider references with particular anchor.
        md_content = md_content.replace(f"]({filename}#", "](#")
        # Then we deal with link to whole pages.
        md_content = md_content.replace(f"]({filename}", f"](#{slug}")

    # Remove contenus additionnels.
    md_content = re.sub(RE_CONTENUS_ADD, "", md_content)
    # Remove everything below references completely
    md_content = md_content.split("\n## Références\n", 1)[0]
    # Avoid numerotation of titles + dynamic titles hierarchy.
    md_content = re.sub(r"## (.*)", rf"{chapter_title_level}# \1 {{-}}", md_content)

    bib_path = textes_path / chapter_id / f"{chapter_id}.bib"
    if bib_path.exists():
        bib_content = bib_path.read_text()
    else:
        bib_content = ""

    # Re-number footnotes to avoid duplicates across chapters.
    md_content = re.sub(r"\[\^(\d+)\]", rf"[^{chapter_id}-\g<1>]", md_content)
    # Add the (unumbered) title per chapter.
    md_content = f"""
{chapter_title_level} {chapter_or_part.title_f} {{-}}

{md_content}
    """
    return md_content, bib_content


def generate_markdown(repository_path, target_path, book):
    print(f"Exporting {target_path} in Markdown:")
    md_contents = ""
    bib_contents = ""

    filenames_to_slugs = {
        f"{chapter.id}.html": slugify(chapter.title_h) for chapter in book.chapters
    }

    for chapter_or_part in book.chapters_and_parts:
        if isinstance(chapter_or_part, Part):
            md_contents += f"\n# {chapter_or_part.title} {{-}}\n\n"

            for chapter in chapter_or_part.chapters:
                if not chapter.pdf:
                    print(f"  Chapter excluded (pdf=false): {chapter.title}")
                    continue

                md_content, bib_content = prepare_chapter_markdown(
                    repository_path, filenames_to_slugs, chapter, within_part=True
                )
                if md_content:
                    md_contents += md_content
                if bib_content:
                    bib_contents += bib_content
        else:  # This is a Chapter.
            if not chapter_or_part.pdf:
                print(f"  Chapter excluded (pdf=false): {chapter_or_part.title}")
                continue

            md_content, bib_content = prepare_chapter_markdown(
                repository_path, filenames_to_slugs, chapter_or_part
            )
            if md_content:
                md_contents += md_content
            if bib_content:
                bib_contents += bib_content

    (target_path / "book.md").write_text(md_contents)
    print(f"  Markdown written in: {target_path / 'book.md'}")
    (target_path / "book.bib").write_text(bib_contents)
    print(f"  Bibliography written in: {target_path / 'book.bib'}")


def generate_pdf(repository_path, template_path, csl_path, target_path, book):
    print(f"Exporting {target_path} in PDF:")
    md_content = (target_path / "book.md").read_text()
    bib_path = target_path / "book.bib"

    extra_args = [
        f"--metadata-file={repository_path / 'textes' / 'garde' / 'livre.yaml'}",
        f"--resource-path={repository_path}:{repository_path / 'textes'}",
        f"--bibliography={bib_path}",
        "--citeproc",
        "--standalone",
    ]
    if book.has_parts:
        extra_args.append("--top-level-division=part")
    else:
        extra_args.append("--top-level-division=chapter")

    if template_path is not None:
        extra_args.append(f"--template={template_path}")
    if csl_path is not None:
        extra_args.append(f"--csl={csl_path}")
    latex_content = pypandoc.convert_text(
        md_content,
        "latex",
        format="markdown+auto_identifiers+ascii_identifiers",
        extra_args=extra_args,
    )
    (target_path / "book.tex").write_text(latex_content)
    print(f"  TEX written in: {target_path / 'book.tex'}")
    extra_args = [
        f"--metadata-file={repository_path / 'textes' / 'garde' / 'livre.yaml'}",
        f"--resource-path={repository_path}:{repository_path / 'textes'}",
        f"--bibliography={bib_path}",
        "--citeproc",
        "--top-level-division=chapter",
        "--pdf-engine=lualatex",
    ]
    if book.has_parts:
        extra_args.append("--top-level-division=part")
    else:
        extra_args.append("--top-level-division=chapter")

    if template_path is not None:
        extra_args.append(f"--template={template_path}")
    pypandoc.convert_text(
        latex_content,
        "pdf",
        format="latex",
        extra_args=extra_args,
        outputfile=str(target_path / "book.pdf"),
    )
    print(f"  PDF written in: {target_path / 'book.pdf'}")
