from dataclasses import dataclass


@dataclass
class Pos:
    line_no: int
    col_no: int


@dataclass
class Diagnostics:
    """
    Represents the information to diagnose problems related to a specific read
    character: At which line and column it was found, and a string with the
    actual line. It also offers functionality to print a human-readable string
    indicating at which place exactly an error occurred.
    """

    pos: Pos
    line: str

    def diagnostic_string(self) -> str:
        if self.line is None:
            raise RuntimeError("No diagnostics for uninitialized state.")

        line_prefix = f"{self.pos.line_no:>5}: "
        output = [line_prefix + self.line]
        arrow_indent = " " * len(line_prefix) + " " * (self.pos.col_no - 1)
        output.append(arrow_indent + "^")
        output.append(arrow_indent + "┗--- here")
        return "\n".join(output)

    def next_col(self) -> "Diagnostics":
        """
        Returns a diagnostics object corresponding to one column advanced
        from the current one. This is to have an object that points to the
        column _after_ the last character, in case there were any missing
        characters such as missing closing quote or closing parenthesis.
        """
        return Diagnostics(Pos(self.pos.line_no, self.pos.col_no + 1), self.line)
