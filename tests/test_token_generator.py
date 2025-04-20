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
from token_generator import token_generator, ScannerError
from charreader import CharReader
from typing import List


class TokenGeneratorTest(unittest.TestCase):
    def assertTokens(self, s: str, *rest):
        expected: List[Token] = list(rest)
        actual: List[Token] = []
        for token in token_generator(CharReader(iter([s]))):
            actual.append(token)

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

    def test_single_comment(self):
        self.assertTokens("//asdf")

    def test_comments(self):
        self.assertTokens(
            "asd // Hello\n// gut *\nvar a = 3;//Test comment ✌️",
            IDENT("asd"),
            VAR(),
            IDENT("a"),
            EQUAL(),
            NUMBER(3.0),
            SEMICOLON(),
        )

    def test_scan_tokens_whitespace(self):
        self.assertTokens(
            '   \t  \n \n (     var ("hund")  \t\n\n\t )   ',
            LPAREN(),
            VAR(),
            LPAREN(),
            STRING("hund"),
            RPAREN(),
            RPAREN(),
        )

    def test_unterminated_string(self):
        generator = token_generator(CharReader(iter(['(var ("hund))'])))
        self.assertEqual(next(generator), LPAREN())
        self.assertEqual(next(generator), VAR())
        self.assertEqual(next(generator), LPAREN())

        with self.assertRaises(ScannerError) as context:
            next(generator)
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
        generator = token_generator(CharReader(iter(["(var ¥)"])))
        next(generator)
        next(generator)
        with self.assertRaises(ScannerError) as context:
            next(generator)
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (var ¥)
            ^
            ┗--- here""",
        )

    def test_illegal_token_emoji(self):
        generator = token_generator(CharReader(iter(["(var 😂)"])))
        next(generator)
        next(generator)
        with self.assertRaises(ScannerError) as context:
            next(generator)
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (var 😂)
            ^
            ┗--- here""",
        )

    def test_error_position_whitespace(self):
        generator = token_generator(CharReader(iter(["(   var   ¥§)"])))
        next(generator)
        next(generator)
        with self.assertRaises(ScannerError) as context:
            next(generator)
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (   var   ¥§)
                 ^
                 ┗--- here""",
        )

    def test_error_position_multiline(self):
        generator = token_generator(CharReader(iter(["(var  \n", "   ¥§)\n"])))
        next(generator)
        next(generator)
        with self.assertRaises(ScannerError) as context:
            next(generator)
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    2:    ¥§)
          ^
          ┗--- here""",
        )
