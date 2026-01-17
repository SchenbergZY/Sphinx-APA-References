import os
from dataclasses import dataclass, field

import sphinxcontrib.bibtex.plugin
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


def copy_stylesheet(app: Sphinx, exc: None) -> None:
    base_dir = os.path.dirname(__file__)
    style = os.path.join(base_dir, "assets", "apastyle.css")

    if app.builder.format == "html" and not exc:
        static_dir = os.path.join(app.builder.outdir, "_static")

        copy_asset_file(style, static_dir)


def override_config(app, config):
    # This runs after the user's conf is read
    config.bibtex_reference_style = "author_year_round"  # override or set


def setup(app):
    app.setup_extension("sphinxcontrib.bibtex")
    sphinxcontrib.bibtex.plugin.register_plugin(
        "sphinxcontrib.bibtex.style.referencing",
        "author_year_round",
        MyReferenceStyle,
    )
    app.add_directive("bibliography", APABibliographyDirective, override=True)
    app.connect("build-finished", copy_stylesheet)
    app.add_css_file("apastyle.css")
    app.connect("config-inited", override_config)
