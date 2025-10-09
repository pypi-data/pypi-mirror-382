from typing import Tuple

from .RAElement import RAElement


class RAOperator(RAElement):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.symbols()[0]
