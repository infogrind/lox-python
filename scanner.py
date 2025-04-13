from tokens import Token, LPAREN, RPAREN, IDENT, EQUAL, STRING
from charreader import CharReader


class ScannerError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _is_ident_char(c: str):
    return c.isalpha() or c == "_"


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
                    f"Unexpected end of string at input {self.char_reader.line_no()}:{self.char_reader.char_no()}"
                )
            c = self.char_reader.next()
            if c == '"':
                break
            chars.append(c)

        return STRING("".join(chars))

    def _scan_ident(self):
        """
        Scans an identifier token from the char reader and returns it.
        If there is a scanning error, a ScannerError is returned instead.
        """
        chars = []
        while True:
            if not self.char_reader.has_next():
                # It is valid for the last token to be an identifier, with nothing following.
                break
            if not _is_ident_char(self.char_reader.peek()):
                # Something else is following
                break
            chars.append(self.char_reader.next())
        return IDENT("".join(chars))

    def _load_next_token(self):
        """
        Scans the next token from the input and assigns it to _next_token. If
        there is an error, the error is assigned instead.
        """
        # Eat any whitespace, detecting the end of the input.
        while True:
            if not self.char_reader.has_next():
                self._next_token = None
                # TODO: Decide if we really want to use None or rather StopIteration.
                #
                # End of input reached.
                return
            if self.char_reader.peek().isspace():
                # Eat the whitespace
                self.char_reader.next()
                continue
            # Found non-whitespace, process actual token.
            break

        c = self.char_reader.peek()
        if c == "(":
            self.char_reader.next()
            self._next_token = LPAREN()
        elif c == ")":
            self.char_reader.next()
            self._next_token = RPAREN()
        elif c == '"':
            self._next_token = self._scan_string()
        elif _is_ident_char(c):
            self._next_token = self._scan_ident()
        else:
            self._next_token = ScannerError(
                f"Invalid token character '{c}' at input {self.char_reader.line_no()}:{self.char_reader.char_no()}"
            )

    def next(self):
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
