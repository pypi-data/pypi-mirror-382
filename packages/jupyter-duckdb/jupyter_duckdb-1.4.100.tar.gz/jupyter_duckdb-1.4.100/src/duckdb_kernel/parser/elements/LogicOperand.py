from typing import Tuple

from .LogicElement import LogicElement
from ..tokenizer import Token
from ..util.RenamableColumnList import RenamableColumnList


class LogicOperand(LogicElement, Tuple[Token]):
    def __new__(cls, *args: Token):
        if not all(t == ',' for i, t in enumerate(args) if i % 2 == 1):
            raise AssertionError('arguments must be separated by commas')

        return super().__new__(
            cls,
            (
                token if not token.endswith(',') else token[:-1]
                for token in args
                if token != ','
            )
        )

    def __str__(self) -> str:
        return ', '.join(self)

    def to_sql(self, cols: RenamableColumnList) -> str:
        # replace " with ' for compatibility with DuckDB
        single_quotes = (t.single_quotes for t in self)

        # replace column names with intermediary ones
        correct_column_names = cols.map_args(single_quotes)

        # join names
        return ', '.join(correct_column_names)
