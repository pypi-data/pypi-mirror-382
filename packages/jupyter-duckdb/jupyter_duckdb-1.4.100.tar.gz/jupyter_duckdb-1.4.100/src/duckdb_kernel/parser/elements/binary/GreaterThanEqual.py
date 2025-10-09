from typing import Tuple

from ..LogicOperator import LogicOperator


class GreaterThanEqual(LogicOperator):
    order = 4000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '≥', '>=', r'gte'

    @property
    def sql_symbol(self) -> str:
        return '>='
