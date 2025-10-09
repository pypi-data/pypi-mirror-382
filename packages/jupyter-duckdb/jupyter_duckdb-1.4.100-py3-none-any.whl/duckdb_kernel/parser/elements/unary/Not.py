from typing import Tuple

from ..LogicElement import LogicElement
from ...util.RenamableColumnList import RenamableColumnList


class Not(LogicElement):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '¬', '!', 'not'

    def __init__(self, target: LogicElement):
        self.target = target

    def __str__(self) -> str:
        target_str = str(self.target)
        if self.target.order > self.order:
            target_str = f'({target_str})'

        return f'{self.symbols()[0]} {target_str}'

    def to_sql(self, cols: RenamableColumnList) -> str:
        return f'NOT ({self.target.to_sql(cols)})'
