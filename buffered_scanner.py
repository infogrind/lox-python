from tokens import Token
from typing import Iterator


class BufferedScanner:
    """
    Scans tokens from the input with a one-token lookahead buffer.
    """

    def __init__(self, token_generator: Iterator[Token]):
        self._token_generator = token_generator

        # Initialize the buffer.
        self._load_next_token()

    def _load_next_token(self):
        """
        Scans the next token from the input and assigns it to _next_token. If
        there is an error, the error is stored instead. We buffer the error, rather
        than direcly re-raising it, such that the user can still call next() or peek()
        for all valid tokens, even if an error will subsequently encountered when
        refilling the buffer.
        """
        try:
            self._next_token = next(self._token_generator)
        except StopIteration:
            # End of input reached.
            self._next_token = None
        except Exception as e:
            self._next_token = e

    def next(self):
        """
        Returns the next scanned token, or an error if no token could be scanned.
        Raises StopIteration if the end of the input has already been reached.
        """
        match self._next_token:
            case Exception():
                raise self._next_token
            case None:
                raise StopIteration
            case _:
                result = self._next_token
                self._load_next_token()
                return result

    def peek(self):
        match self._next_token:
            case Exception():
                raise self._next_token
            case None:
                raise StopIteration
            case _:
                return self._next_token

    def has_next(self):
        return self._next_token is not None
