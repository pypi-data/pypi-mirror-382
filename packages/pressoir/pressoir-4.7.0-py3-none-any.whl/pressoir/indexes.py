import locale
from collections import defaultdict

import unidecode
from jinja2 import Environment as Env
from jinja2 import FileSystemLoader
from jinja2.exceptions import FilterArgumentError
from jinja2.filters import ignore_case
from selectolax.parser import HTMLParser

from . import ROOT_DIR
from .utils import generate_md5

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# This is the jinja2 configuration to locate templates.
environment = Env(loader=FileSystemLoader(str(ROOT_DIR / "templates")))
# Useful for dates rendering within Jinja2.
locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")


def do_dictsortunicode(value, case_sensitive=False, by="key", reverse=False):
    """Same as built-in dictsort but order accentuated words the right way.

    Inspired by
    https://github.com/pallets/jinja/blob/27c65757b26bb5012df1a5ccab1340cd7d52f139/
    src/jinja2/filters.py#L257
    """
    if by == "key":
        pos = 0
    elif by == "value":
        pos = 1
    else:
        raise FilterArgumentError('You can only sort by either "key" or "value"')

    def sort_func(item):
        value = item[pos]

        if not case_sensitive:
            value = ignore_case(value)

        # This is where we remove accents from the string.
        value = unidecode.unidecode(value)

        # And where we strip the markdown emphasis.
        value = value.replace("*", "")

        return value

    return sorted(value.items(), key=sort_func, reverse=reverse)


environment.filters["dictsortunicode"] = do_dictsortunicode


def do_markdownem(value):
    if "*" in value:
        pre, text = value.split("*", 1)
        if "*" in text:
            term, post = text.split("*", 1)
            value = f"{pre}<em>{term}</em>{post}"
    return value


environment.filters["markdownem"] = do_markdownem


def collect_index_and_update_attrs(chapter_id, html, kind, ids, refs):
    for item in html.css(f"h4.{kind},span.{kind}"):
        idsp = item.attributes.get("data-idsp")
        glossaire_id = item.attributes.get("data-idglossaire")
        if idsp is None:
            idsp = item.text()
        idsp_id = f"{kind}-{generate_md5(idsp)}"
        # In place modification of the item by selectolax (class addition).
        item.attrs["class"] = f"{item.attrs['class']} {idsp_id}"
        if chapter_id in refs[idsp]:
            refs[idsp][chapter_id] += 1
            # Ensure we only add the same id once per page.
            continue
        refs[idsp][chapter_id] = 1
        ids[kind][idsp] = {
            "idsp_id": idsp_id,
            "glossaire_id": glossaire_id,
        }
        # In place modification of the item by selectolax (id addition).
        item.attrs["id"] = idsp_id


def collect_indexes_and_add_ids(target, book, kinds):
    ids = defaultdict(dict)
    refs = defaultdict(dict)
    for chapter in book.chapters:
        chapter_id = chapter.id
        html_file = target / f"{chapter_id}.html"
        if not html_file.exists():
            break
        html_content = html_file.read_text()
        parsed_html = HTMLParser(html_content)
        for kind, title in kinds.items():
            collect_index_and_update_attrs(chapter_id, parsed_html, kind, ids, refs)
        html_file.write_text(parsed_html.html)
    return ids, refs


def generate_index(ids, refs, kinds):
    template = environment.get_template("index.html")
    return template.render(ids=ids, refs=refs, kinds=kinds)


def write_index(output, content):
    index_html = output.read_text()
    index_html = index_html.replace("%INDEX%", content)
    output.write_text(index_html)


def generate_indexes(repository_path, target_path, book):
    """Generate the index page and related ids."""
    print(f"Generating indexes for {repository_path}")
    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )
    kinds = dict(
        zip(book_settings["indexes"]["ids"], book_settings["indexes"]["names"])
    )
    ids, refs = collect_indexes_and_add_ids(target_path, book, kinds)
    index_content = generate_index(ids, refs, kinds)
    index_file = target_path / "index-np.html"
    if index_file.exists():
        write_index(index_file, index_content)
