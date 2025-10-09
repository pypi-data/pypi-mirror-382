from typing import Tuple

from ..LogicOperator import LogicOperator


class ArrowLeft(LogicOperator):
    order = 3000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '←', '<-'
