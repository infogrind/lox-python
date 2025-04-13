from typing import Iterator


class CharReader:
    """
    A reader to read characters from successive lines. Offers a peek()
    functionality for lookahead.
    """

    def __init__(self, line_iter: Iterator[str]):
        self.line_iter = line_iter
        self._load_line()
        self._load_char()

    def _load_line(self):
        """
        Loads the next line from the input iterator into head_line and resets
        the char_iter. If the input iterator has no more elements, head_line is
        set to None.
        """
        while True:
            try:
                self.head_line = next(self.line_iter)
                self.char_iter = iter(self.head_line)
            except StopIteration:
                # End of lines reached
                self.head_line = None
                return
            if self.head_line != "":
                # Found next non-empty line.
                break
            # Continue to skip empty lines.

    def _load_char(self):
        """
        Loads the next character from the current line into head_char, to make
        it accessible by peek(). If there are no more characters, head_char is
        set to none.
        """
        if self.head_line is None:
            # No more lines in line iterator, therefore also no more characters.
            self.head_char = None
            return
        try:
            self.head_char = next(self.char_iter)
        except StopIteration:
            # First see if there is another line to read.
            self._load_line()
            if self.head_line is None:
                # We have reached the end of characters and lines.
                self.head_char = None
            else:
                try:
                    self.head_char = next(self.char_iter)
                except StopIteration:
                    # We must have read an empty line. That is a bug, because load_line should skip
                    # empty lines.
                    raise RuntimeError("Illegal state detected, probably a bug.")

    def next(self) -> str:
        """
        Returns the next character and advances to the next character.
        Raises StopIteration if there are no more characters.
        """
        if self.head_char is None:
            raise StopIteration

        result = self.head_char
        self._load_char()
        return result

    def has_next(self) -> bool:
        """
        Returns True if there is still a character to read, false otherwise.
        """
        return self.head_char is not None

    def peek(self) -> str:
        """
        Returns the character that would be returned by a call to next(),
        without advancing. Raises StopIteration if there is no more character
        to read.
        """
        if self.head_char is None:
            raise StopIteration
        return self.head_char
