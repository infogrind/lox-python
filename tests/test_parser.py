import unittest

from ast_printer import print_program
from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from diagnostics import Pos
from parser import ParserError, parse_program
from syntax import Program
from token_generator import token_generator


def parse_string(s: str) -> Program:
    return parse_program(
        BufferedScanner(BufferedIterator(token_generator(CharReader(iter([s])))))
    )


class TestParser(unittest.TestCase):
    def assertParses(self, s: str, r: str) -> None:
        self.assertEqual(
            print_program(
                parse_program(
                    BufferedScanner(
                        BufferedIterator(token_generator(CharReader(iter([s]))), 2)
                    )
                )
            ),
            r,
        )

    def test_empty_program(self):
        self.assertParses("", "")

    # Expressions

    def test_true_literal(self):
        self.assertParses("true;", "true")

    def test_false_literal(self):
        self.assertParses("false;", "false")

    def test_nil_literal(self):
        self.assertParses("nil;", "nil")

    def test_number_literal(self):
        self.assertParses("12.34;", "12.34")

    def test_string_literal(self):
        self.assertParses('"foosdf I";', "foosdf I")

    def test_grouping(self):
        self.assertParses("( 3 );", "3.0")

    def test_equal_equal(self):
        self.assertParses("true == false;", "( == true false )")

    def test_bang_equal(self):
        self.assertParses("true != false;", "( != true false )")

    def test_less_than(self):
        self.assertParses("true < false;", "( < true false )")

    def test_less_equal(self):
        self.assertParses("true <= false;", "( <= true false )")

    def test_greater_than(self):
        self.assertParses("true > false;", "( > true false )")

    def test_nested_parentheses(self):
        self.assertParses(
            "true > (true != (true == false)  );",
            "( > true ( != true ( == true false ) ) )",
        )

    def test_precedence_without_parentheses(self):
        self.assertParses(
            "1 + 2 * 3 - 4 / 5;", "( - ( + 1.0 ( * 2.0 3.0 ) ) ( / 4.0 5.0 ) )"
        )

    def test_comparison_equality_precedence(self):
        self.assertParses("true == false > true;", "( == true ( > false true ) )")
        self.assertParses("true == false <= true;", "( == true ( <= false true ) )")
        self.assertParses("true != false > true;", "( != true ( > false true ) )")
        self.assertParses("true != false <= true;", "( != true ( <= false true ) )")

    def test_comparison_equality_grouping(self):
        self.assertParses(
            "((true < false) == (false >= true)) > ((false != true) != (true));",
            "( > ( == ( < true false ) ( >= false true ) ) ( != ( != false true ) true ) )",
        )

    def test_addition(self):
        self.assertParses("2 + 3;", "( + 2.0 3.0 )")

    def test_subtraction(self):
        self.assertParses("2 - 3;", "( - 2.0 3.0 )")

    def test_unary_expressions(self):
        self.assertParses("-2;", "( - 2.0 )")
        self.assertParses("!true;", "( ! true )")
        self.assertParses("1 + 2 * - 3;", "( + 1.0 ( * 2.0 ( - 3.0 ) ) )")
        self.assertParses(
            "1 + 2 * - 7 + 5 - !(true > false);",
            "( - ( + ( + 1.0 ( * 2.0 ( - 7.0 ) ) ) 5.0 ) ( ! ( > true false ) ) )",
        )

    def test_repeated_unary_expressions(self):
        self.assertParses("!!true;", "( ! ( ! true ) )")
        self.assertParses("--2;", "( - ( - 2.0 ) )")

    # Statements

    def test_print_stmt(self):
        self.assertParses("print(1 + 2);", "( print ( + 1.0 2.0 ) )")

    def test_multi_statement_program(self):
        self.assertParses(
            """\
1 + 2;
print(23);
true;
print(2 * (8 + 2));""",
            """\
( + 1.0 2.0 )
( print 23.0 )
true
( print ( * 2.0 ( + 8.0 2.0 ) ) )""",
        )

    def test_expr_with_variables(self):
        self.assertParses("a + b * c / d;", "( + a ( / ( * b c ) d ) )")

    # Variables

    def test_empty_vardecl(self):
        self.assertParses("var a;", "( var a )")

    def test_vardecl_with_literal(self):
        self.assertParses("var a = 3;", "( var a 3.0 )")

    def test_assignment(self):
        self.assertParses("a = 3;", "( = a 3.0 )")

    def test_decl_and_assignment(self):
        self.assertParses("var a; a = 2;", "( var a )\n( = a 2.0 )")

    def test_variable_expression(self):
        self.assertParses("a;", "a")

    def test_assignment_from_variable(self):
        self.assertParses("a = b;", "( = a b )")

    def test_nested_assignment(self):
        self.assertParses("a = b = c;", "( = a ( = b c ) )")

    def test_complex_nested_assignment(self):
        self.assertParses(
            "a = b + (3 / (a = 7));", "( = a ( + b ( / 3.0 ( = a 7.0 ) ) ) )"
        )

    def test_invalid_lvalue(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("3 + a = 5;")
        self.assertEqual(ctx.exception.message, "Invalid lvalue")

    # Error cases

    def test_lonely_plus(self):
        with self.assertRaises(ParserError) as context:
            parse_string("1 + ( + 2)")
        self.assertEqual(context.exception.message, "Illegal start of expression")
        self.assertEqual(context.exception.diagnostics.pos, Pos(1, 7))

    def test_unclosed_parenthesis(self):
        with self.assertRaises(ParserError) as context:
            parse_string("1 + (2 * (3 - 9)")
        self.assertEqual(context.exception.message, "Missing closing parenthesis")
        self.assertEqual(context.exception.diagnostics.pos, Pos(1, 17))

    def test_invalid_multiple_expressions(self):
        with self.assertRaises(ParserError) as context:
            parse_string("(1 + 3) (4 + 5)")
        self.assertEqual(
            context.exception.message, "Missing semicolon after expression statement"
        )
