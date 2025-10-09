from typing import Tuple

from ..LogicOperator import LogicOperator


class Equal(LogicOperator):
    order = 5000

    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '=',
