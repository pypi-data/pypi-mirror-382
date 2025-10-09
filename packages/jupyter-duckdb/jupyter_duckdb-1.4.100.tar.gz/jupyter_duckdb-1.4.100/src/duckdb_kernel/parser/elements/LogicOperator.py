from typing import Tuple

from .LogicElement import LogicElement
from ..util.RenamableColumnList import RenamableColumnList


class LogicOperator(LogicElement):
    @staticmethod
    def symbols() -> Tuple[str]:
        raise NotImplementedError

    def __init__(self, left: LogicElement, right: LogicElement):
        self.left: LogicElement = left
        self.right: LogicElement = right

    @property
    def text_symbol(self) -> str:
        return self.symbols()[0]

    @property
    def sql_symbol(self) -> str:
        return self.text_symbol

    def __str__(self) -> str:
        left_str = str(self.left)
        if self.left.order > self.order:
            left_str = f'({left_str})'

        right_str = str(self.right)
        if self.right.order > self.order:
            right_str = f'({right_str})'

        return f'{left_str} {self.text_symbol} {right_str}'

    def to_sql(self, cols: RenamableColumnList) -> str:
        return f'({self.left.to_sql(cols)}) {self.sql_symbol} ({self.right.to_sql(cols)})'
