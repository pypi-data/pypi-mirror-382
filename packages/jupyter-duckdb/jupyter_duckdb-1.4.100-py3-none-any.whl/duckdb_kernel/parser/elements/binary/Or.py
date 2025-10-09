from typing import Tuple

from ..LogicOperator import LogicOperator


class Or(LogicOperator):
    order = 7000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '∨', 'or'

    @property
    def sql_symbol(self) -> str:
        return 'OR'
