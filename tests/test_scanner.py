import unittest
from tokens import Token, LPAREN, RPAREN, IDENT, EQUAL, STRING
from scanner import Scanner, ScannerError
from charreader import CharReader


class ScannerTest(unittest.TestCase):
    def test_scan_tokens(self):
        scanner = Scanner(CharReader(iter(['(var ("hund"))'])))
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), IDENT("var"))
        self.assertEqual(scanner.next(), IDENT("var"))
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), STRING("hund"))
        self.assertEqual(scanner.next(), STRING("hund"))
        self.assertEqual(scanner.peek(), RPAREN())
        self.assertEqual(scanner.peek(), RPAREN())
        self.assertEqual(scanner.next(), RPAREN())
        self.assertEqual(scanner.next(), RPAREN())

        self.assertFalse(scanner.has_next())

    def test_scan_tokens_whitespace(self):
        scanner = Scanner(
            CharReader(iter(['   \t  \n \n (     var ("hund")  \t\n\n\t )   ']))
        )
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), IDENT("var"))
        self.assertEqual(scanner.next(), IDENT("var"))
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), STRING("hund"))
        self.assertEqual(scanner.next(), STRING("hund"))
        self.assertEqual(scanner.peek(), RPAREN())
        self.assertEqual(scanner.peek(), RPAREN())
        self.assertEqual(scanner.next(), RPAREN())
        self.assertEqual(scanner.next(), RPAREN())

        self.assertFalse(scanner.has_next())

    def test_scan_tokens_multiline(self):
        # Same input as above, but split into lines with newline characters.
        scanner = Scanner(CharReader(iter(["(var (\n", '"hund"))\n'])))
        self.assertEqual(scanner.peek(), LPAREN())
        self.assertEqual(scanner.next(), LPAREN())
        self.assertEqual(scanner.peek(), IDENT("var"))
        self.assertEqual(scanner.next(), IDENT("var"))
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
        self.assertEqual(scanner.next(), IDENT("var"))
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
        scanner = Scanner(CharReader(iter(["(var 27)"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (var 27)
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
        scanner = Scanner(CharReader(iter(["(   var   27)"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    1: (   var   27)
                 ^
                 ┗--- here""",
        )

    def test_error_position_multiline(self):
        scanner = Scanner(CharReader(iter(["(var  \n", "   27)\n"])))
        scanner.next()
        scanner.next()
        with self.assertRaises(ScannerError) as context:
            scanner.next()
        self.assertEqual(
            str(context.exception),
            """\
Invalid token character:
    2:    27)
          ^
          ┗--- here""",
        )
