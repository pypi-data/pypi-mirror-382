from selectolax.parser import HTMLParser


def convert_sidenotes(html_content):
    """Converts sidenotes for TufteCSS."""
    parsed_html = HTMLParser(html_content)
    sidenotes = parsed_html.css(".footnote-ref")
    for count, sidenote in enumerate(sidenotes, start=1):
        # Get the first parent section, Pandoc generates invalid HTML
        # with duplicated ids for sidenotes when generated for main
        # content and additional contents. We try to be more selective
        # and generate our own custom sidenote ref.
        custom_sidenote_id = f"sidenote-{count}"
        custom_sidenote_ref = f"sidenote-ref-{count}"
        sidenote_id = sidenote.attributes["id"]

        parent_section = sidenote.parent
        while parent_section.css_first(sidenote.attributes["href"]) is None:
            parent_section = parent_section.parent

        sidenote_ref = parent_section.css_first(sidenote.attributes["href"])
        sidenote_ref.unwrap_tags(["p"])
        sidenote_content = sidenote_ref.html
        sidenote_content = sidenote_content.replace("<li ", '<span class="sidenote"')
        sidenote_content = sidenote_content.replace("</li>", "</span>")
        parsed_sidenote_content = HTMLParser(sidenote_content)
        sidenote_ref_id = parsed_sidenote_content.body.child.attributes["id"]
        sidenote_content = sidenote_content.replace(
            f'id="{sidenote_ref_id}"', f'id="{custom_sidenote_id}"'
        )
        sidenote_content = sidenote_content.replace(
            f'href="#{sidenote_id}"', f'href="#{custom_sidenote_ref}"'
        )
        # replace_with from selectolax only allows a Node,
        # otherwise it will escape the tags! Hence the extra-parsing.
        tufte_sidenote = HTMLParser(
            (
                # Do not add more spaces between HTML elements otherwise
                # it leads to orphans in the body of the text.
                f"<span>"
                f'<label for="{custom_sidenote_ref}" class="margin-toggle '
                'sidenote-number"></label>'
                f'<input type="checkbox" id="{custom_sidenote_ref}" '
                'class="margin-toggle">'
                f"{sidenote_content}"
                f"</span>"
            )
        )
        tufte_sidenote_span = tufte_sidenote.css_first("span")
        sidenote.replace_with(tufte_sidenote_span)
    for footnote in parsed_html.css(".footnotes"):
        footnote.remove()
    return parsed_html.html


def rewrite_global_sidenotes(html_content):
    # We try to avoid ids matching the ones from additional contents.
    html_content = (
        html_content.replace('id="fn', 'id="global-fn')
        .replace('href="#fn', 'href="#global-fn')
        .replace('id="fnref', 'id="global-fnref')
        .replace('href="#fnref', 'href="#global-fnref')
    )
    return html_content
