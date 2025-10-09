from typing import Tuple

from ..LogicOperator import LogicOperator


class Unequal(LogicOperator):
    order = 5000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '≠', '!='

    @property
    def sql_symbol(self) -> str:
        return '!='
