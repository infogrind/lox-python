import unittest
from parser import parse_node, ParserError
from ast_printer import print_node
from token_generator import token_generator
from charreader import CharReader
from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from syntax import Node


def parse_string(s: str) -> Node:
    return parse_node(
        BufferedScanner(BufferedIterator(token_generator(CharReader(iter([s])))))
    )


class TestParser(unittest.TestCase):
    def assertParses(self, s: str, r: str) -> None:
        self.assertEqual(
            print_node(
                parse_node(
                    BufferedScanner(
                        BufferedIterator(token_generator(CharReader(iter([s]))), 2)
                    )
                )
            ),
            r,
        )

    def test_true_literal(self):
        self.assertParses("true", "true")

    def test_false_literal(self):
        self.assertParses("false", "false")

    def test_nil_literal(self):
        self.assertParses("nil", "nil")

    def test_number_literal(self):
        self.assertParses("12.34", "12.34")

    def test_string_literal(self):
        self.assertParses('"foosdf I"', "foosdf I")

    def test_grouping(self):
        self.assertParses("( 3 )", "3.0")

    def test_equal_equal(self):
        self.assertParses("true == false", "( == true false )")

    def test_bang_equal(self):
        self.assertParses("true != false", "( != true false )")

    def test_less_than(self):
        self.assertParses("true < false", "( < true false )")

    def test_less_equal(self):
        self.assertParses("true <= false", "( <= true false )")

    def test_greater_than(self):
        self.assertParses("true > false", "( > true false )")

    def test_nested_parentheses(self):
        self.assertParses(
            "true > (true != (true == false)  )",
            "( > true ( != true ( == true false ) ) )",
        )

    def test_precedence_without_parenteses(self):
        self.assertParses(
            "1 + 2 * 3 - 4 / 5", "( - ( + 1.0 ( * 2.0 3.0 ) ) ( / 4.0 5.0 ) )"
        )

    def test_comparison_equality_precedence(self):
        self.assertParses("true == false > true", "( == true ( > false true ) )")
        self.assertParses("true == false <= true", "( == true ( <= false true ) )")
        self.assertParses("true != false > true", "( != true ( > false true ) )")
        self.assertParses("true != false <= true", "( != true ( <= false true ) )")

    def test_comparison_equality_grouping(self):
        self.assertParses(
            "((true < false) == (false >= true)) > ((false != true) != (true))",
            "( > ( == ( < true false ) ( >= false true ) ) ( != ( != false true ) true ) )",
        )

    def test_addition(self):
        self.assertParses("2 + 3", "( + 2.0 3.0 )")

    def test_subtraction(self):
        self.assertParses("2 - 3", "( - 2.0 3.0 )")

    # Error cases

    def test_lonely_plus(self):
        with self.assertRaises(ParserError) as context:
            parse_string("1 + ( + 2)")
        self.assertEqual(
            str(context.exception),
            """\
Illegal start of expression:
    1: 1 + ( + 2)
             ^
             ┗--- here""",
        )

    def test_unclosed_parentesis(self):
        with self.assertRaises(ParserError) as context:
            parse_string("1 + (2 * (3 - 9)")
        self.assertEqual(
            str(context.exception),
            """\
Missing closing parenthesis:
    1: 1 + (2 * (3 - 9)
                      ^
                      ┗--- here
Starting parenthesis:
    1: 1 + (2 * (3 - 9)
           ^
           ┗--- here""",
        )
