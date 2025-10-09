from typing import Tuple

from ..LogicOperator import LogicOperator


class GreaterThan(LogicOperator):
    order = 4000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '>', r'gt'
