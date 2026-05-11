import unittest

from pybtex.database import parse_string
from pybtex.plugin import find_plugin

from sphinx_apa_references import APANoInbookPagePrefixStyle, register_plugins


def render_entry(entry_type, pages, style_class=APANoInbookPagePrefixStyle):
    bib_data = parse_string(
        f"""
        @{entry_type}{{sample,
            author = {{Doe, Jane}},
            editor = {{Smith, John}},
            title = {{A Sample Chapter}},
            booktitle = {{A Sample Book}},
            journal = {{A Sample Journal}},
            publisher = {{Example Press}},
            year = {{2024}},
            pages = {{{pages}}},
        }}
        """,
        "bibtex",
    )
    entry = bib_data.entries["sample"]
    formatted = style_class().format_entry("sample", entry)
    return formatted.text.render_as("text")


class InbookPageFormattingTests(unittest.TestCase):
    def test_inbook_pages_do_not_render_page_prefix(self):
        rendered = render_entry("inbook", "12-34")

        self.assertRegex(rendered, r"A Sample Book, 12[-\u2013]34")
        self.assertNotRegex(rendered, r"A Sample Book \([^\)]*12[-\u2013]34\)")
        self.assertNotIn("pp. 12", rendered)
        self.assertNotIn("pp 12", rendered)
        self.assertNotIn("p. 12", rendered)

    def test_page_prefix_is_unchanged_for_other_entry_types(self):
        rendered = render_entry("article", "12-34")

        self.assertIn("pp.", rendered)

    def test_extension_registers_custom_apa_formatter(self):
        register_plugins()

        registered_style = find_plugin("pybtex.style.formatting", "apa")

        self.assertIs(registered_style, APANoInbookPagePrefixStyle)

    def test_registered_apa_formatter_removes_inbook_page_prefix(self):
        register_plugins()
        registered_style = find_plugin("pybtex.style.formatting", "apa")

        rendered = render_entry("inbook", "12-34", registered_style)

        self.assertRegex(rendered, r"A Sample Book, 12[-\u2013]34")
        self.assertNotRegex(rendered, r"A Sample Book \([^\)]*12[-\u2013]34\)")
        self.assertNotIn("pp. 12", rendered)


if __name__ == "__main__":
    unittest.main()
