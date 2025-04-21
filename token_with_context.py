from dataclasses import dataclass
from tokens import Token


@dataclass
class TokenWithContext:
    t: Token
    d: str  # diagnostic message
