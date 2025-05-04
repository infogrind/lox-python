import io
import unittest
from contextlib import contextmanager
from typing import Generator
from unittest.mock import patch

from main import main


class TestMain(unittest.TestCase):
    def assertOutputs(self, input: str, output: str) -> None:
        with (
            patch("sys.stdin", io.StringIO(input)),
            patch("sys.stdout", new=io.StringIO()) as fake_out,
            patch("sys.argv", ["main.py"]),
        ):
            main()
            actual_output = fake_out.getvalue()

        self.assertEqual(actual_output, output)

    def test_smoke(self):
        self.assertOutputs(
            "print(3+4 * 2 > 10.9 == (nil == nil));",
            """\
Enter some code (ctrl-d to exit):
> True
> """,
        )

    def test_syntax_error(self):
        self.assertOutputs(
            "(1 + 2",
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
        self.assertOutputs(
            '"hello',
            """\
Enter some code (ctrl-d to exit):
> Unexpected end of string:
    1: "hello
             ^
             ┗--- here
> """,
        )

    def test_type_error(self):
        self.assertOutputs(
            "1 + true;",
            """\
Enter some code (ctrl-d to exit):
> Expected: number:
    1: 1 + true;
           ^
           ┗--- here
> """,
        )

    def test_undefined_variable(self):
        self.assertOutputs(
            "print(1 + a);",
            """\
Enter some code (ctrl-d to exit):
> 'a' not defined:
    1: print(1 + a);
                 ^
                 ┗--- here
> """,
        )

    def test_variable_type_error(self):
        self.assertOutputs(
            "var a = 77;\nprint(true == a);",
            """\
Enter some code (ctrl-d to exit):
> > Cannot compare <class 'bool'> and <class 'float'>:
    1: print(true == a);
                  ^
                  ┗--- here
> """,
        )
