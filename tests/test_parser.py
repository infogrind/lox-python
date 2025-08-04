import unittest

from ast_printer import print_program
from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from diagnostics import Pos
from parser import ParserError, parse_program
from syntax import Program
from token_generator import ScannerError, token_generator


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
            "1 + 2;\nprint(23);\ntrue;\nprint(2 * (8 + 2));",
            "( + 1.0 2.0 )\n( print 23.0 )\ntrue\n( print ( * 2.0 ( + 8.0 2.0 ) ) )",
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

    def test_empty_block(self):
        self.assertParses("{}", "{ }")

    def test_block_with_single_statement(self):
        self.assertParses("{ 42; }", "{ 42.0; }")

    def test_block_with_multiple_statements(self):
        self.assertParses("{ 1; 2; 3; }", "{ 1.0; 2.0; 3.0; }")

    def test_block_with_variable_declaration(self):
        self.assertParses("{ var x = 5; }", "{ ( var x 5.0 ); }")

    def test_nested_blocks(self):
        self.assertParses("{ { 1; } }", "{ { 1.0; }; }")

    def test_block_with_mixed_declarations(self):
        self.assertParses(
            "{ var x = 1; print(x); var y = 2; }",
            "{ ( var x 1.0 ); ( print x ); ( var y 2.0 ); }",
        )

    def test_unclosed_block(self):
        with self.assertRaises(ParserError) as context:
            parse_string("{ 1; 2;")
        self.assertEqual(context.exception.message, "Expected '}' after block")

    def test_if_statement(self):
        self.assertParses("if (true) 1;", "( if true 1.0 )")

    def test_if_else_statement(self):
        self.assertParses("if (true) 1; else 2;", "( if true 1.0 else 2.0 )")

    def test_nested_if_statement(self):
        self.assertParses(
            "if (true) if (false) 1; else 2;",
            "( if true ( if false 1.0 else 2.0 ) )",
        )

    def test_if_with_block(self):
        self.assertParses("if (true) { 1; }", "( if true { 1.0; } )")

    def test_if_else_with_blocks(self):
        self.assertParses(
            "if (true) { 1; } else { 2; }", "( if true { 1.0; } else { 2.0; } )"
        )

    def test_block_missing_opening_brace(self):
        with self.assertRaises(ParserError) as context:
            parse_string("1; }")
        self.assertEqual(
            context.exception.message, "Unexpected token RBRACE() while parsing primary"
        )

    def test_deeply_nested_expression(self):
        self.assertParses(
            "((((1 + 2) * 3) - 4) / 5) == 6;",
            "( == ( / ( - ( * ( + 1.0 2.0 ) 3.0 ) 4.0 ) 5.0 ) 6.0 )",
        )

    def test_left_associativity(self):
        self.assertParses("1 - 2 - 3;", "( - ( - 1.0 2.0 ) 3.0 )")

    def test_assignment_associativity(self):
        self.assertParses("a = b = c = d;", "( = a ( = b ( = c d ) ) )")

    def test_dangling_else(self):
        self.assertParses("if (a) if (b) c; else d;", "( if a ( if b c else d ) )")

    def test_if_without_then(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("if (true);")
        self.assertEqual(
            ctx.exception.message, "Unexpected token SEMICOLON() while parsing primary"
        )

    def test_missing_variable_name(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("var = 10;")
        self.assertEqual(ctx.exception.message, "Unexpected token")

    def test_assignment_to_literal(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("123 = 456;")
        self.assertEqual(ctx.exception.message, "Invalid lvalue")

    def test_missing_semicolon_after_vardecl(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("var a = 1")
        self.assertEqual(
            ctx.exception.message, "Missing semicolon after variable declaration"
        )

    def test_mismatched_parentheses(self):
        with self.assertRaises(ScannerError) as ctx:
            parse_string("(1 + 2];")
        self.assertEqual(ctx.exception.message, "Invalid token character")

    def test_logical_and(self):
        self.assertParses("true and false;", "( and true false )")

    def test_logical_or(self):
        self.assertParses("true or false;", "( or true false )")

    def test_logical_precedence(self):
        self.assertParses("a or b and c or d;", "( or ( or a ( and b c ) ) d )")

    # While loops

    def test_simple_while(self):
        self.assertParses("while (true) {}", "( while true { } )")

    def test_while_with_multiple_statements(self):
        self.assertParses(
            "while (true) { a = a + 1; print(a); }",
            "( while true { ( = a ( + a 1.0 ) ); ( print a ); } )",
        )

    def test_while_with_complex_condition(self):
        self.assertParses(
            "while (a >= 2 and b <= 4) print(a);",
            "( while ( and ( >= a 2.0 ) ( <= b 4.0 ) ) ( print a ) )",
        )

    def test_while_with_missing_opening_parenthesis(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("while a >= 1")
        self.assertEqual(ctx.exception.message, "Expected '(' after 'while'")

    def test_while_with_missing_closing_parenthesis(self):
        with self.assertRaises(ParserError) as ctx:
            parse_string("while (a >= 1 print(a);")
        self.assertIn("Expected ')'", ctx.exception.message)
