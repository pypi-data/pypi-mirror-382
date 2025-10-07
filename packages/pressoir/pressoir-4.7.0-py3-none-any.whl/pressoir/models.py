from dataclasses import dataclass, field
from datetime import date

from dataclass_wizard import DumpMeta, YAMLWizard
from yaml.composer import ComposerError

from . import VERSION
from .utils import strip_html_tags


@dataclass
class Author:
    forname: str
    surname: str
    orcidurl: str = ""
    presentation: str = ""
    display: bool = None
    institution: str = ""
    foaf: str = ""
    isni: str = ""
    orcid: str = ""
    viaf: str = ""
    wikidata: str = ""
    affiliations: str = ""
    email: str = ""
    biography: str = ""


@dataclass
class Book(YAMLWizard):
    version: int
    title: str
    lang: str
    date: date
    rights: str
    url: str
    collective: bool
    coverurl: str
    abstract_fr: str
    abstract_en: str
    keyword_fr: str
    keyword_en: str
    isbnprint: str
    isbnepub: str
    isbnpdf: str
    isbnnum: str
    publisher: str
    place: str

    # (Re)Filled in a second step.
    authors: list
    toc: list
    chapters: list = None
    chapters_and_parts: list = None
    has_search: bool = False
    title_h: str = None
    title_f: str = None
    subtitle: str = None
    subtitle_f: str = None
    nbpages: str = None
    date_french: str = None
    zoteroDescription: str = "Accéder à cette bibliographie sur Zotero"
    pressoir_version: str = VERSION
    url_publisher: str = ""
    productor: str = ""
    productor_num: str = ""
    diffusor: str = ""
    pdfurl: str = ""
    epuburl: str = ""
    luluurl: str = ""

    year: str = ""
    month: str = ""
    day: str = ""

    @property
    def has_parts(self):
        return len(self.chapters) != len(self.chapters_and_parts)

    def __post_init__(self):
        self.title_h = self.title_h or self.title
        self.title_f = self.title_f or strip_html_tags(self.title)
        self.subtitle_f = self.subtitle_f or strip_html_tags(self.subtitle)

        dataclass_authors = []
        for author in self.authors:
            dataclass_authors.append(Author(**author))
        self.authors = dataclass_authors

        self.year, self.month, self.day = self.date.isoformat().split("-")


@dataclass
class Part:
    title: str
    chapters: list = None


@dataclass
class Chapter(YAMLWizard):
    title: str
    abstract_fr: str = ""
    abstract_en: str = ""
    keyword_fr: str = ""
    keyword_en: str = ""

    # (Re)Filled in a second step.
    authors: list = field(default_factory=list)
    translators: list = field(default_factory=list)

    id: str = None
    title_h: str = None
    title_f: str = None
    subtitle: str = None
    subtitle_f: str = None
    part: Part = None
    blockcitation: bool = None
    pdf: bool = True
    is_not_search: bool = True
    url_traduction: str = ""
    url: str = ""
    url_relative: str = ""
    zoteroCollection: str = ""
    lang: str = ""
    search_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.title_h = self.title_h or self.title
        self.title_f = self.title_f or strip_html_tags(self.title)
        self.subtitle_f = self.subtitle_f or strip_html_tags(self.subtitle)

        dataclass_authors = []
        for author in self.authors:
            dataclass_authors.append(Author(**author))
        self.authors = dataclass_authors

        dataclass_translators = []
        for translator in self.translators:
            dataclass_translators.append(Author(**translator))
        self.translators = dataclass_translators


def configure_book(yaml_path):
    # Preserves abstract_fr key for instance (vs. abstract-fr) when converting to_yaml()
    DumpMeta(key_transform="SNAKE").bind_to(Book)
    DumpMeta(key_transform="SNAKE").bind_to(Chapter)

    try:
        book = Book.from_yaml_file(yaml_path)
    except ComposerError:
        book = Book.from_yaml(yaml_path.read_text().split("---")[1])
    repository_path = yaml_path.parent.parent
    book.chapters_and_parts = configure_chapters_and_parts(book, repository_path)
    only_chapters = []
    for chapter_or_part in book.chapters_and_parts:
        if isinstance(chapter_or_part, Chapter):
            only_chapters.append(chapter_or_part)
        elif isinstance(chapter_or_part, Part):
            for chapter in chapter_or_part.chapters:
                only_chapters.append(chapter)
    book.chapters = only_chapters
    book.has_search = "recherche" in [chap.id for chap in book.chapters]
    return book


def configure_chapters_and_parts(book, repository_path):
    dataclass_chapters = []
    for chapter in book.toc:
        if "id" in chapter:
            dataclass_chapters.append(
                configure_chapter(book, chapter["id"], repository_path)
            )
        elif "parttitle" in chapter:
            part = Part(title=chapter["parttitle"])
            dataclass_chapters.append(part)
            part_chapters = []
            for chap in chapter["content"]:
                part_chapters.append(
                    configure_chapter(book, chap["id"], repository_path)
                )
            part.chapters = part_chapters
    return dataclass_chapters


def configure_chapter(book, chapter_id, repository_path):
    try:
        chapter = Chapter.from_yaml_file(
            repository_path / chapter_id / f"{chapter_id}.yaml"
        )
    except ComposerError:
        chapter = Chapter.from_yaml(
            (repository_path / chapter_id / f"{chapter_id}.yaml")
            .read_text()
            .split("---")[1]
        )

    chapter.id = chapter_id
    chapter.url = f"{book.url}{chapter_id}.html"
    chapter.url_relative = f"{chapter_id}.html"
    chapter.is_not_search = "recherche" != chapter_id
    return chapter
