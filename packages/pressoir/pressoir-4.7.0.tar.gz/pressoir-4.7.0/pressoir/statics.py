import shutil

from slugify import slugify

from . import ROOT_DIR
from .utils import each_file_from, generate_md5

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def sync_media(repository_path, target_path, book):
    if not (repository_path / "pressoir").exists():
        print(f"The `pressoir` folder is missing from `{repository_path}`.")
        exit(1)

    media_path = repository_path / "textes" / "media"
    if media_path.exists():
        shutil.copytree(media_path, target_path / "media", dirs_exist_ok=True)
    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )
    # Copy the PDF file if defined in `pressoir/book.toml` as `media.pdf_path`
    # to the `pdfurl` target in `livre.yaml` if defined too.
    if media := book_settings.get("media"):
        if pdf_path := media.get("pdf_path"):
            if pdf_url := book.pdfurl.lstrip("./"):
                shutil.copy(repository_path / pdf_path, target_path / pdf_url)


def sync_statics(repository_path, target_path):
    if not (repository_path / "pressoir").exists():
        print(f"The `pressoir` folder is missing from `{repository_path}`.")
        exit(1)
    shutil.copytree(
        repository_path / "pressoir" / "static" / "fonts",
        target_path / "static" / "fonts",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        ROOT_DIR / "static" / "svg",
        target_path / "static" / "svg",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        repository_path / "pressoir" / "static" / "svg",
        target_path / "static" / "svg",
        dirs_exist_ok=True,
    )
    shutil.copytree(
        ROOT_DIR / "static" / "img",
        target_path / "static" / "img",
        dirs_exist_ok=True,
    )
    img_path = repository_path / "pressoir" / "static" / "img"
    if img_path.exists():
        shutil.copytree(img_path, target_path / "static" / "img", dirs_exist_ok=True)

    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )
    if theme := book_settings.get("theme"):
        for svg_file in each_file_from(target_path / "static" / "svg", pattern="*.svg"):
            replacements = theme.get(slugify(svg_file.name))
            if replacements:
                svg_content = svg_file.read_text()
                svg_content = svg_content.replace(replacements[0], replacements[1])
                svg_file.write_text(svg_content)


def bundle_statics(repository_path, target_path):
    pressoir_settings = tomllib.loads((ROOT_DIR / "project.toml").read_text())
    book_settings = tomllib.loads(
        (repository_path / "pressoir" / "book.toml").read_text()
    )
    theme = book_settings.get("theme")
    indexes = book_settings.get("indexes")

    css_parts = []
    for css_file in pressoir_settings["statics"]["css_files"]:
        css_parts.append(f"/* {css_file} */")
        css_parts.append((ROOT_DIR / css_file).read_text())
    for css_file in book_settings["statics"]["css_files"]:
        css_parts.append(f"/* {css_file} */")
        css_content = (repository_path / "pressoir" / css_file).read_text()
        # Dynamic CSS variables replacements from `book.toml[theme]`.
        if theme and css_file.endswith("vars.css"):
            for key, [initial, replacement] in theme.items():
                source = f"--{key}: {initial};"
                target = f"--{key}: {replacement};"
                css_content = css_content.replace(source, target)
        # Dynamic CSS addition for indexes from `book.toml[indexes]`.
        if indexes and css_file.endswith("custom.css"):
            for index, image in zip(indexes["ids"], indexes["images"]):
                css_content = f"""
                    .termeenrichi.{index} {{
                        background-image: url("{image}");
                    }}
                    {css_content}
                """
        css_parts.append(css_content)

    js_parts = []
    for js_file in pressoir_settings["statics"]["js_files"]:
        js_parts.append(f"/* {js_file} */")
        js_parts.append((ROOT_DIR / js_file).read_text())
    for js_file in book_settings["statics"].get("js_files", []):
        js_parts.append(f"/* {js_file} */")
        js_parts.append((repository_path / "pressoir" / js_file).read_text())

    css_content = "\n".join(css_parts)
    css_filename = f"bundle.{generate_md5(css_content)}.css"
    (target_path / "static" / css_filename).write_text(css_content)

    js_content = "\n".join(js_parts)
    js_filename = f"bundle.{generate_md5(js_content)}.js"
    (target_path / "static" / js_filename).write_text(js_content)

    return css_filename, js_filename
