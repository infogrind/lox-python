import unittest
import io
from unittest.mock import patch
from main import main


class TestMain(unittest.TestCase):
    def test_smoke(self):
        with (
            patch("sys.stdin", io.StringIO("3+4 * 2 > 10.9 == (nil == nil)")),
            patch("sys.stdout", new=io.StringIO()) as fake_out,
            patch("sys.argv", ["main.py"]),
        ):
            main()
            actual_output = fake_out.getvalue()

        self.assertEqual(
            actual_output,
            """\
Enter some code (ctrl-d to exit):
> True
> """,
        )
