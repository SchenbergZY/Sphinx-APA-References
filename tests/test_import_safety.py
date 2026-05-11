import os
import subprocess
import sys
import textwrap
import unittest


class ImportSafetyTests(unittest.TestCase):
    def test_import_ignores_broken_firstlast_entry_point(self):
        code = textwrap.dedent(
            """
            import pybtex.plugin

            class BrokenEntryPoint:
                def load(self):
                    raise AttributeError(
                        "module 'teachbooks.plugins.pybtex.names' "
                        "has no attribute 'FirstLastStyle'"
                    )

            original_entry_points = pybtex.plugin.entry_points

            def entry_points_with_broken_firstlast(**params):
                if (
                    params.get("group") == "pybtex.style.names"
                    and params.get("name") == "firstlast"
                ):
                    return [BrokenEntryPoint()]
                return original_entry_points(**params)

            pybtex.plugin.entry_points = entry_points_with_broken_firstlast

            import sphinx_apa_references

            print(sphinx_apa_references.APANoInbookPagePrefixStyle.__name__)
            """
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = "src" + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("APANoInbookPagePrefixStyle", result.stdout)


if __name__ == "__main__":
    unittest.main()
