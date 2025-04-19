import unittest
from tokens import (
    Token,
    LPAREN,
    RPAREN,
    LBRACE,
    RBRACE,
    COMMA,
    DOT,
    MINUS,
    PLUS,
    SEMICOLON,
    SLASH,
    STAR,
    BANG,
    BANG_EQUAL,
    EQUAL,
    EQUAL_EQUAL,
    GREATER,
    GREATER_EQUAL,
    LESS,
    LESS_EQUAL,
    IDENT,
    STRING,
    NUMBER,
    AND,
    CLASS,
    ELSE,
    FALSE,
    FUN,
    FOR,
    IF,
    NIL,
    OR,
    PRINT,
    RETURN,
    SUPER,
    THIS,
    TRUE,
    VAR,
    WHILE,
)
from scanner import Scanner, ScannerError
from charreader import CharReader
from typing import List


class ScannerTest(unittest.TestCase):
    def assertTokens(self, s: str, *rest):
        expected: List[Token] = list(rest)
        actual: List[Token] = []
        scanner = Scanner(CharReader(iter([s]), 2))
        while scanner.has_next():
            actual.append(scanner.next())

        self.assertEqual(actual, expected)

    def test_skip_whitespace(self):
        self.assertTokens("(  \n )\n\n)", LPAREN(), RPAREN(), RPAREN())

    def test_single_character_tokens(self):
        self.assertTokens("()", LPAREN(), RPAREN())
        self.assertTokens("{}", LBRACE(), RBRACE())
        self.assertTokens(".,*", DOT(), COMMA(), STAR())
        self.assertTokens("-+", MINUS(), PLUS())
        self.assertTokens(";/*", SEMICOLON(), SLASH(), STAR())

    def test_one_or_two_character_tokens(self):
        self.assertTokens("= == == =", EQUAL(), EQUAL_EQUAL(), EQUAL_EQUAL(), EQUAL())
        # Maximum munch rule: identify the longest fitting token.
        self.assertTokens("====", EQUAL_EQUAL(), EQUAL_EQUAL())
        self.assertTokens("===", EQUAL_EQUAL(), EQUAL())
        self.assertTokens("! !=", BANG(), BANG_EQUAL())
        self.assertTokens("!!!", BANG(), BANG(), BANG())
        self.assertTokens("!!=", BANG(), BANG_EQUAL())
        self.assertTokens(
            "!!!====", BANG(), BANG(), BANG_EQUAL(), EQUAL_EQUAL(), EQUAL()
        )
        self.assertTokens("<>", LESS(), GREATER())
        self.assertTokens("<<>>", LESS(), LESS(), GREATER(), GREATER())
        self.assertTokens("<=>=", LESS_EQUAL(), GREATER_EQUAL())
        self.assertTokens("<====", LESS_EQUAL(), EQUAL_EQUAL(), EQUAL())
        self.assertTokens("<<=", LESS(), LESS_EQUAL())

    def test_strings(self):
        self.assertTokens(
            '"hund""jesus" "frank"""""',
            STRING("hund"),
            STRING("jesus"),
            STRING("frank"),
            STRING(""),
            STRING(""),
        )

    def test_numbers(self):
        self.assertTokens("12.34", NUMBER(12.34))
        self.assertTokens("1234", NUMBER(1234))
        self.assertTokens(".1234", DOT(), NUMBER(1234))
        self.assertTokens("1234.abc", NUMBER(1234), DOT(), IDENT("abc"))

    def test_identifiers(self):
        self.assertTokens(
            "foo bar baz _hello _sMugi13_3__31",
            IDENT("foo"),
            IDENT("bar"),
            IDENT("baz"),
            IDENT("_hello"),
            IDENT("_sMugi13_3__31"),
        )

    def test_keywords(self):
        self.assertTokens(
            "and class else false fun for if nil or",
            AND(),
            CLASS(),
            ELSE(),
            FALSE(),
            FUN(),
            FOR(),
            IF(),
            NIL(),
            OR(),
        )
        self.assertTokens(
            "print return super this true var while",
            PRINT(),
            RETURN(),
            SUPER(),
            THIS(),
            TRUE(),
            VAR(),
            WHILE(),
        )

    def test_keywords_are_case_sensitive(self):
        self.assertTokens(
            "and aND class claSS", AND(), IDENT("aND"), CLASS(), IDENT("claSS")
        )

    def test_crazy_token_combinations(self):
        self.assertTokens(
            "234.-classseven_!class.seven",
            NUMBER(234.0),
            DOT(),
            MINUS(),
            IDENT("classseven_"),
            BANG(),
            CLASS(),
            DOT(),
            IDENT("seven"),
        )

    def test_scan_tokens_whitespace(self):
        scanner = Scanner(
            CharReader(iter(['   \t  \n \n (     var ("hund")  \t\n\n\t )   ']))
        )
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), VAR())
        self.assertEqual(scanner.next(), VAR())
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), STRING("hund"))
        self.assertEqual(scanner.next(), STRING("hund"))
        self.assertEqual(scanner.peek(), RPAREN())
        self.assertEqual(scanner.peek(), RPAREN())
        self.assertEqual(scanner.next(), RPAREN())
        self.assertEqual(scanner.next(), RPAREN())

        self.assertFalse(scanner.has_next())

    def test_unterminated_string(self):
        scanner = Scanner(CharReader(iter(['(var ("hund))'])))
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.next(), VAR())
        self.assertEqual(scanner.next(), LPAREN())

        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Unexpected end of string:
    1: (var ("hund))
                   ^
                   ┗--- here\
""",
        )

    def test_illegal_token(self):
        scanner = Scanner(CharReader(iter(["(var ¥)"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (var ¥)
            ^
            ┗--- here""",
        )

    def test_illegal_token_emoji(self):
        scanner = Scanner(CharReader(iter(["(var 😂)"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (var 😂)
            ^
            ┗--- here""",
        )

    def test_error_position_whitespace(self):
        scanner = Scanner(CharReader(iter(["(   var   ¥§)"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (   var   ¥§)
                 ^
                 ┗--- here""",
        )

    def test_error_position_multiline(self):
        scanner = Scanner(CharReader(iter(["(var  \n", "   ¥§)\n"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    2:    ¥§)
          ^
          ┗--- here""",
        )
