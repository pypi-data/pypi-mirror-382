from typing import Tuple

from ..LogicOperator import LogicOperator


class LessThanEqual(LogicOperator):
    order = 4000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '≤', '<=', r'lte'

    @property
    def sql_symbol(self) -> str:
        return '<='
