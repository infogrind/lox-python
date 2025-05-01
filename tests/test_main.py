import io
import unittest
from unittest.mock import patch

from main import main


class TestMain(unittest.TestCase):
    def test_smoke(self):
        with (
            patch("sys.stdin", io.StringIO("3+4 * 2 > 10.9 == (nil == nil);")),
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

    def test_syntax_error(self):
        with (
            patch("sys.stdin", io.StringIO("(1 + 2")),
            patch("sys.stdout", new=io.StringIO()) as fake_out,
            patch("sys.argv", ["main.py"]),
        ):
            main()
            actual_output = fake_out.getvalue()

        self.assertEqual(
            actual_output,
            """\
Enter some code (ctrl-d to exit):
> Missing closing parenthesis:
    1: (1 + 2
             ^
             ┗--- here
Opening parenthesis here:
    1: (1 + 2
       ^
       ┗--- here
> """,
        )

    def test_scanner_error(self):
        with (
            patch("sys.stdin", io.StringIO('"hello')),
            patch("sys.stdout", new=io.StringIO()) as fake_out,
            patch("sys.argv", ["main.py"]),
        ):
            main()
            actual_output = fake_out.getvalue()

        self.assertEqual(
            actual_output,
            """\
Enter some code (ctrl-d to exit):
> Unexpected end of string:
    1: "hello
             ^
             ┗--- here
> """,
        )

    def test_type_error(self):
        with (
            patch("sys.stdin", io.StringIO("1 + true;")),
            patch("sys.stdout", new=io.StringIO()) as fake_out,
            patch("sys.argv", ["main.py"]),
        ):
            main()
            actual_output = fake_out.getvalue()

        self.assertEqual(
            actual_output,
            """\
Enter some code (ctrl-d to exit):
> Expected: number:
    1: 1 + true;
           ^
           ┗--- here
> """,
        )
