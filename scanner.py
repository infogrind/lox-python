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


class ScannerError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _is_ident_start_char(c: str):
    return c.isalpha() or c == "_"


def _is_ident_cont_char(c: str):
    return c.isalnum() or c == "_"


class Scanner:
    def __init__(self, char_reader: CharReader):
        self.char_reader = char_reader
        self._load_next_token()

    def _scan_string(self):
        """
        Scans a string token from the char reader and returns it.
        If there is a scanning error, a ScannerError is returned instead.
        """
        chars = []
        # Eat first quote
        self.char_reader.next()
        while True:
            if not self.char_reader.has_next():
                return ScannerError(
                    "\n".join(
                        [
                            "Unexpected end of string:",
                            self.char_reader.diagnostic_string(),
                        ]
                    )
                )
            c = self.char_reader.next()
            if c == '"':
                break
            chars.append(c)

        return STRING("".join(chars))

    def _scan_number(self):
        """
        Scans a number, which can be 1234 or 12.34, but not 12. or .34.
        """
        digits = []
        # First everything before a potential decimal point.
        while self.char_reader.has_next() and self.char_reader.peek().isdigit():
            digits.append(self.char_reader.next())

        # Check for decimal point followed by more digits.
        if (
            not self.char_reader.has_next()
            or not self.char_reader.can_peek(1)
            or self.char_reader.peek(0) != "."
            or not self.char_reader.peek(1).isdigit()
        ):
            # The condition for a decimal part are not present, so we exit early.
            return NUMBER(float("".join(digits)))

        # Process the decimal part, which we now know is there.
        digits.append(self.char_reader.next())  # This is the decimal point.
        while self.char_reader.has_next() and self.char_reader.peek().isdigit():
            digits.append(self.char_reader.next())

        return NUMBER(float("".join(digits)))

    def _scan_ident_or_keyword(self):
        """
        Scans an identifier token from the char reader and returns it.
        If there is a scanning error, a ScannerError is returned instead.
        """
        chars = [self.char_reader.next()]
        while True:
            if not self.char_reader.has_next():
                # It is valid for the last token to be an identifier, with nothing following.
                break
            if not _is_ident_cont_char(self.char_reader.peek()):
                # Something else is following
                break
            chars.append(self.char_reader.next())

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

    def _eat_comment(self) -> None:
        c = self.char_reader
        assert c.eat("/")
        assert c.eat("/")
        while c.has_next():
            # The comment ends with a new line character (or with end of input).
            if c.eat("\n"):
                return

            # Eat any other comment charater.
            c.next()

        # If we're at the end, we need to clear the next token.
        self._next_token = None

    def _scan_token(self) -> Token | ScannerError:
        """
        For better ergonomics, core token scanning functionality is encapsulated
        in this function, which returns the tokens rather than assigning it to
        some instance variable.
        """

        # Just an alias for better ergonomics.
        c = self.char_reader

        # Single character tokens
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
            return self._scan_string()
        elif c.peek().isdigit():
            return self._scan_number()
        elif _is_ident_start_char(c.peek()):
            return self._scan_ident_or_keyword()
        else:
            return ScannerError(
                "\n".join(
                    ["Invalid token character:", self.char_reader.diagnostic_string()]
                )
            )

    def _load_next_token(self):
        """
        Scans the next token from the input and assigns it to _next_token. If
        there is an error, the error is assigned instead.

        This is where the main logic is.
        """
        c = self.char_reader
        # Eat any whitespace, detecting the end of the input.
        while True:
            if not c.has_next():
                self._next_token = None
                # TODO: Decide if we really want to use None or rather StopIteration.
                #
                # End of input reached.
                return
            if c.peek().isspace():
                # Eat the whitespace
                c.next()
                continue

            # Check for comments and skip them.
            if c.can_peek(1) and c.peek(0) == "/" and c.peek(1) == "/":
                self._eat_comment()

                # There could again be whitespace or a comment afterwards.
                continue

            # Don't try to process more if the comment was at the end of the
            # input.
            if not c.has_next():
                return
            # Found non-whitespace, process actual token.
            break

        self._next_token = self._scan_token()

    def next(self):
        """
        Returns the next scanned token, or an error if no token could be scanned.
        Raises StopIteration if the end of the input has already been reached.
        """
        match self._next_token:
            case ScannerError():
                raise self._next_token
            case None:
                raise StopIteration
            case _:
                result = self._next_token
                self._load_next_token()
                return result

    def peek(self):
        if self._next_token is None:
            raise StopIteration
        return self._next_token

    def has_next(self):
        return self._next_token is not None
