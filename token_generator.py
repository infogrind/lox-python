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
from charreader import CharReader
from typing import Generator
from token_with_context import TokenWithContext


class ScannerError(Exception):
    """
    Custom exception to store a scanning error.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _is_ident_start_char(c: str):
    """
    Defines what characters an identifier can start with.
    """
    return c.isalpha() or c == "_"


def _is_ident_cont_char(c: str):
    """
    Defines allowed characters an identifier can have in positions after the first.
    """
    return c.isalnum() or c == "_"


def _skip_whitespace(c: CharReader) -> None:
    """
    Eats all whitespace from the CharReader until (and excluding)
    the first non-whitespace character.
    """
    while c.has_next() and c.peek().isspace():
        c.next()


def _skip_comments(c: CharReader) -> None:
    """
    Eats all comments in the input until either then input ends or there
    is something else than a comment.
    """
    while True:
        if not c.can_peek(1) or not (c.peek(0) == "/" and c.peek(1) == "/"):
            # Fewer than two characters left or no comment.
            return

        # Eat the entire comment until an end-of-line is found or the input ends.
        while c.has_next() and not c.eat("\n"):
            c.next()


def _scan_string(c: CharReader) -> Token:
    """
    Scans a string token from the char reader and returns it.
    If there is a scanning error, a ScannerError is returned instead.
    """
    chars = []
    # Eat first quote
    c.next()
    while True:
        if not c.has_next():
            raise ScannerError(
                "\n".join(
                    [
                        "Unexpected end of string:",
                        c.diagnostic_string(),
                    ]
                )
            )
        char = c.next()
        if char == '"':
            break
        chars.append(char)

    return STRING("".join(chars))


def _scan_number(c: CharReader) -> Token:
    """
    Scans a number, which can be 1234 or 12.34, but not 12. or .34.
    """
    digits = []
    # First everything before a potential decimal point.
    while c.has_next() and c.peek().isdigit():
        digits.append(c.next())

    # Check for decimal point followed by more digits.
    if (
        not c.has_next()
        or not c.can_peek(1)
        or c.peek(0) != "."
        or not c.peek(1).isdigit()
    ):
        # The condition for a decimal part are not present, so we exit early.
        return NUMBER(float("".join(digits)))

    # Process the decimal part, which we now know is there.
    digits.append(c.next())  # This is the decimal point.
    while c.has_next() and c.peek().isdigit():
        digits.append(c.next())

    return NUMBER(float("".join(digits)))


def _scan_ident_or_keyword(c: CharReader) -> Token:
    """
    Scans an identifier token from the char reader and returns it. If the
    string matches a keyword, returns a keyword token instead.
    """
    chars = [c.next()]
    while True:
        if not c.has_next():
            # It is valid for the last token to be an identifier, with nothing following.
            break
        if not _is_ident_cont_char(c.peek()):
            # Something else is following
            break
        chars.append(c.next())

    ident = "".join(chars)

    # Identify reserved words as keywords. If it's not a keyword, then it's
    # an identifier.
    if ident == "and":
        return AND()
    elif ident == "class":
        return CLASS()
    elif ident == "else":
        return ELSE()
    elif ident == "false":
        return FALSE()
    elif ident == "fun":
        return FUN()
    elif ident == "for":
        return FOR()
    elif ident == "if":
        return IF()
    elif ident == "nil":
        return NIL()
    elif ident == "or":
        return OR()
    elif ident == "print":
        return PRINT()
    elif ident == "return":
        return RETURN()
    elif ident == "super":
        return SUPER()
    elif ident == "this":
        return THIS()
    elif ident == "true":
        return TRUE()
    elif ident == "var":
        return VAR()
    elif ident == "while":
        return WHILE()
    else:
        return IDENT(ident)


def _scan_token(c: CharReader) -> Token:
    """
    Reads the next token from the given CharReader and returns it.

    Raises a ScannerError if invalid input is encountered.
    """
    if c.eat("("):
        return LPAREN()
    elif c.eat(")"):
        return RPAREN()
    elif c.eat("{"):
        return LBRACE()
    elif c.eat("}"):
        return RBRACE()
    elif c.eat(","):
        return COMMA()
    elif c.eat("."):
        return DOT()
    elif c.eat("-"):
        return MINUS()
    elif c.eat("+"):
        return PLUS()
    elif c.eat(";"):
        return SEMICOLON()
    elif c.eat("/"):
        return SLASH()
    elif c.eat("*"):
        return STAR()

    # One or two character token
    elif c.eat("="):
        return EQUAL_EQUAL() if c.eat("=") else EQUAL()
    elif c.eat("!"):
        return BANG_EQUAL() if c.eat("=") else BANG()
    elif c.eat("<"):
        return LESS_EQUAL() if c.eat("=") else LESS()
    elif c.eat(">"):
        return GREATER_EQUAL() if c.eat("=") else GREATER()

    # Literals and keywords
    elif c.peek() == '"':
        return _scan_string(c)
    elif c.peek().isdigit():
        return _scan_number(c)
    elif _is_ident_start_char(c.peek()):
        return _scan_ident_or_keyword(c)
    else:
        raise ScannerError(
            "\n".join(["Invalid token character:", c.diagnostic_string()])
        )


def token_generator(char_reader: CharReader) -> Generator[TokenWithContext, None, None]:
    """
    Returns a generator that produces tokens scanned from the input.

    This function implements the core scanner logic.
    """
    while char_reader.has_next():
        _skip_whitespace(char_reader)
        _skip_comments(char_reader)

        # The whitespace skipping or commend skipping could have ended due to end of
        # input, so we need to check for that.
        if not char_reader.has_next():
            break

        # Scan next actual token.
        diag_str = char_reader.diagnostic_string()
        token = _scan_token(char_reader)
        yield TokenWithContext(token, diag_str)
