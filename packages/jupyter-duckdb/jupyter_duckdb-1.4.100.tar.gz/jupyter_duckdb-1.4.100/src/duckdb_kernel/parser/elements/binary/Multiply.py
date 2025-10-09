from typing import Tuple

from ..LogicOperator import LogicOperator


class Multiply(LogicOperator):
    order = 1000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '*',
