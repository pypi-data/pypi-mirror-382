from typing import Tuple

from ..LogicOperator import LogicOperator


class Minus(LogicOperator):
    order = 2000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '-',
