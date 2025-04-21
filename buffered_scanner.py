from buffered_iterator import BufferedIterator
from tokens import Token
from token_with_context import TokenWithContext


class BufferedScanner:
    def __init__(self, bit: BufferedIterator[TokenWithContext]) -> None:
        self._bit = bit

    def has_next(self) -> bool:
        return self._bit.has_next()

    def next(self) -> Token:
        self._latest_diag = self._bit.peek().d
        return self._bit.next().t

    def can_peek(self, offset: int = 0) -> bool:
        return self._bit.can_peek(offset)

    def peek(self, offset: int = 0) -> Token:
        return self._bit.peek(offset).t

    def eat(self, t: Token) -> bool:
        if self._bit.has_next() and self._bit.peek().t == t:
            self._bit.next()
            return True

        return False

    def diagnostics(self) -> str:
        if self._bit.has_next():
            return self._bit.peek().d
        else:
            return self._latest_diag
