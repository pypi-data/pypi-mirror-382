from typing import Tuple

from ..LogicOperator import LogicOperator


class Divide(LogicOperator):
    order = 1000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '/', '÷'

    @property
    def sql_symbol(self) -> str:
        return '/'
