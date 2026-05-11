import os
import re
from dataclasses import dataclass, field

import pybtex.plugin
import sphinxcontrib.bibtex.plugin
from names.firstlast import NameStyle as APAFirstLastNameStyle

# formatting.apa resolves firstlast at import time, so pin the matching
# pybtex-apa-style name plugin before other distributions can shadow it.
pybtex.plugin.register_plugin(
    "pybtex.style.names",
    "firstlast",
    APAFirstLastNameStyle,
    force=True,
)

from formatting.apa import APAStyle, date, editor_names
from pybtex.richtext import Symbol, Text
from pybtex.style.formatting import toplevel
from pybtex.style.template import FieldIsMissing, node
from pybtex.style.template import field as template_field
from pybtex.style.template import join, optional, optional_field, sentence
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file
from sphinxcontrib.bibtex.directives import BibliographyDirective
from sphinxcontrib.bibtex.style.referencing import BracketStyle
from sphinxcontrib.bibtex.style.referencing.author_year import \
    AuthorYearReferenceStyle


class APABibliographyDirective(BibliographyDirective):
    """Same as BibliographyDirective, but forces style='apa'."""

    def run(self):
        # ensure 'style' option is set to 'apa' unless user overrides it
        self.options.setdefault("style", "apa")
        nodes = super().run()
        print(nodes[0].children)
        return nodes


def bracket_style() -> BracketStyle:
    return BracketStyle(
        left="(",
        right=")",
    )


@dataclass
class MyReferenceStyle(AuthorYearReferenceStyle):
    bracket_parenthetical: BracketStyle = field(default_factory=bracket_style)
    bracket_textual: BracketStyle = field(default_factory=bracket_style)
    bracket_author: BracketStyle = field(default_factory=bracket_style)
    bracket_label: BracketStyle = field(default_factory=bracket_style)
    bracket_year: BracketStyle = field(default_factory=bracket_style)


def format_pages_without_prefix(text):
    page_parts = re.split(r"[-\u2012\u2013\u2014\u2015]+", str(text))
    return Text(Symbol("ndash")).join(page_parts)


pages_without_prefix = template_field(
    "pages",
    apply_func=format_pages_without_prefix,
)


@node
def inbook_details_without_parentheses(children, context, **kwargs):
    assert not children

    entry = context["entry"]
    parts = []

    edition = entry.fields.get("edition")
    if edition:
        parts.append(Text(edition, " ed."))

    volume = entry.fields.get("volume")
    if volume:
        parts.append(Text("Vol.", Symbol("nbsp"), volume))

    pages = entry.fields.get("pages")
    if pages:
        parts.append(format_pages_without_prefix(pages))

    if not parts:
        raise FieldIsMissing("pages", entry)

    return Text(", ").join(parts)


class APANoInbookPagePrefixStyle(APAStyle):
    """APA style with unprefixed page ranges for inbook entries."""

    def get_inbook_template(self, e):
        # Required fields: author/editor, title, chapter/pages, publisher, year
        # Optional fields: volume, series, address, edition, month, note, key
        return toplevel[
            sentence(sep=" ")[
                self.format_names("author"),
                join["(", date, ")"],
            ],
            self.format_title(e, "title"),
            sentence(sep=" ")[
                optional[
                    "In ",
                    editor_names(),
                    ",",
                ],
                join[
                    self.format_btitle(e, "booktitle", as_sentence=False),
                    optional[", ", inbook_details_without_parentheses()],
                ],
            ],
            sentence(sep=": ")[
                optional_field("address"),
                template_field("publisher"),
            ],
            sentence[optional_field("note")],
        ]


def copy_stylesheet(app: Sphinx, exc: None) -> None:
    base_dir = os.path.dirname(__file__)
    style = os.path.join(base_dir, "assets", "apastyle.css")

    if app.builder.format == "html" and not exc:
        static_dir = os.path.join(app.builder.outdir, "_static")

        copy_asset_file(style, static_dir)


def override_config(app, config):
    # This runs after the user's conf is read
    config.bibtex_reference_style = "author_year_round"  # override or set


def register_plugins():
    sphinxcontrib.bibtex.plugin.register_plugin(
        "sphinxcontrib.bibtex.style.referencing",
        "author_year_round",
        MyReferenceStyle,
        force=True,
    )
    pybtex.plugin.register_plugin(
        "pybtex.style.formatting",
        "apa",
        APANoInbookPagePrefixStyle,
        force=True,
    )


def setup(app):
    app.setup_extension("sphinxcontrib.bibtex")
    register_plugins()
    app.add_directive("bibliography", APABibliographyDirective, override=True)
    app.connect("build-finished", copy_stylesheet)
    app.add_css_file("apastyle.css")
    app.connect("config-inited", override_config)
