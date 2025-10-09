from typing import Tuple

from ..LogicOperator import LogicOperator


class Add(LogicOperator):
    order = 2000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '+',
