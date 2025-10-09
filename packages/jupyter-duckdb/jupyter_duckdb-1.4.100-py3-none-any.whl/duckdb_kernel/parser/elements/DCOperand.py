from typing import Tuple

from .LogicOperand import LogicOperand
from ..ParserError import DCParserError
from ..tokenizer import Token


class DCOperand(LogicOperand):
    def __new__(cls, relation: Token, columns: Tuple[Token, ...], skip_comma: bool = False, depth: int = 0):
        if not skip_comma and not all(t == ',' for i, t in enumerate(columns) if i % 2 == 1):
            raise DCParserError('arguments must be separated by commas', 0)

        return tuple.__new__(
            cls,
            (relation, *(
                token if not token.endswith(',') else token[:-1]
                for token in columns
                if token != ','
            ))
        )

    def __init__(self, relation: Token, columns: Tuple[Token, ...], skip_comma: bool = False, depth: int = 0):
        super().__init__()

        self.depth: int = depth
        self.invert: bool = False

    @property
    def relation(self) -> Token:
        return self[0]

    @property
    def names(self) -> Tuple[Token]:
        return self[1:]

    def __str__(self) -> str:
        columns = ', '.join(self.names)
        return f'{self.relation}({columns})'
