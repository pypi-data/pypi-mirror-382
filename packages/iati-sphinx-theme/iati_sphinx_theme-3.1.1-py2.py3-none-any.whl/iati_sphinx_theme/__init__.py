"""A sphinx theme for IATI documentation sites."""

from datetime import datetime
from os import path
from typing import Any

import sphinx.application
from docutils import nodes
from docutils.parsers.rst.states import Inliner
from sphinx.writers.html5 import HTML5Translator

SUPPORTED_LANGUAGES = {
    "en": "English",
    "fr": "Français",
    "es": "Español",
}


def iati_reference_role(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: dict[str, Any] = {},
    content: list[Any] = [],
) -> tuple[list[nodes.Node], list[Any]]:
    node = nodes.inline(text=text)
    node["classes"].append("iati-reference")
    return [node], []


class table_wrapper(nodes.General, nodes.Element):
    """Container node for wrapping tables in divs."""

    pass


def wrap_tables_in_container(
    app: sphinx.application.Sphinx, doctree: nodes.document, docname: str
) -> None:
    """Wrap all table nodes in a custom container node for design system styling."""
    for table in doctree.traverse(nodes.table):
        # Unwrap paragraphs inside table cells for cleaner HTML
        for entry in table.traverse(nodes.entry):
            # If the cell contains only a single paragraph, unwrap it
            if len(entry.children) == 1 and isinstance(
                entry.children[0], nodes.paragraph
            ):
                para = entry.children[0]
                entry.children = para.children

        wrapper = table_wrapper()
        table.replace_self(wrapper)
        wrapper.append(table)


def visit_table_wrapper(self: HTML5Translator, node: nodes.Node) -> None:
    """Render opening div tag for table wrapper."""
    self.body.append('<div class="iati-table">\n')


def depart_table_wrapper(self: HTML5Translator, node: nodes.Node) -> None:
    """Render closing div tag for table wrapper."""
    self.body.append("</div>\n")


def setup(app: sphinx.application.Sphinx) -> dict[str, Any]:
    app.add_html_theme("iati_sphinx_theme", path.abspath(path.dirname(__file__)))
    app.config["html_permalinks_icon"] = "#"
    app.config["html_favicon"] = "static/favicon-16x16.png"
    app.config["html_context"]["language"] = app.config["language"]
    app.config["html_context"]["current_year"] = datetime.now().year
    enabled_languages = app.config["html_theme_options"].get("languages", ["en"])
    app.config["html_context"]["languages"] = {
        code: value
        for code, value in SUPPORTED_LANGUAGES.items()
        if code in enabled_languages
    }
    app.add_js_file("language-switcher.js")
    locale_path = path.join(path.abspath(path.dirname(__file__)), "locale")
    app.add_message_catalog("sphinx", locale_path)
    app.add_role("iati-reference", iati_reference_role)

    # Register custom node and event to wrap tables in div.iati-table
    # for design system compatibility
    app.add_node(table_wrapper, html=(visit_table_wrapper, depart_table_wrapper))
    app.connect("doctree-resolved", wrap_tables_in_container)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
