from typing import Tuple

from ..LogicOperator import LogicOperator


class And(LogicOperator):
    order = 6000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '∧', 'and', 'and'

    @property
    def sql_symbol(self) -> str:
        return 'AND'
