import unittest
from diagnostics import Diagnostics, Pos


class DiagnosticsTest(unittest.TestCase):
    def test_diagnostic_message(self):
        self.assertEqual(
            Diagnostics(Pos(23, 3), "a + b * c + x").diagnostic_string(),
            """\
   23: a + b * c + x
         ^
         ┗--- here""",
        )
