import unittest
from parser import parse_expression
from ast_printer import print_expression
from token_generator import token_generator
from charreader import CharReader
from buffered_iterator import BufferedIterator


class TestParser(unittest.TestCase):
    def assertParses(self, s: str, r: str) -> None:
        self.assertEqual(
            print_expression(
                parse_expression(
                    BufferedIterator(token_generator(CharReader(iter([s]))), 2)
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

    def test_comparison_equality_precedence(self):
        self.assertParses("true == false > true", "( == true ( > false true ) )")
        self.assertParses("true == false <= true", "( == true ( <= false true ) )")
        self.assertParses("true != false > true", "( != true ( > false true ) )")
        self.assertParses("true != false <= true", "( != true ( <= false true ) )")

    def test_complex_grouping(self):
        self.assertParses(
            "((true < false) == (false >= true)) > ((false != true) != (true))",
            "( > ( == ( < true false ) ( >= false true ) ) ( != ( != false true ) true ) )",
        )
