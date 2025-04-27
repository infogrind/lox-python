from dataclasses import dataclass
from tokens import Token
from charreader import Diagnostics


@dataclass
class TokenWithContext:
    t: Token
    d: Diagnostics
