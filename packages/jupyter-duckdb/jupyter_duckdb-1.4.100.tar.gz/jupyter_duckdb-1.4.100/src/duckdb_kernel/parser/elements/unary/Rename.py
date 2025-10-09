from typing import Tuple, Dict

from duckdb_kernel.db import Table
from ..LogicElement import LogicElement
from ..RAElement import RAElement
from ..RAUnaryOperator import RAUnaryOperator
from ..binary import ArrowLeft
from ...util.RenamableColumnList import RenamableColumnList


class Rename(RAUnaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return 'β', 'beta'

    def __init__(self, target: RAElement, arg: ArrowLeft):
        if not isinstance(arg, ArrowLeft):
            raise AssertionError('only arrow statements allowed as parameter')

        super().__init__(target)
        self.arrow: ArrowLeft = arg

    @property
    def arg(self) -> LogicElement:
        return self.arrow

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subquery
        subquery, subcols = self.target.to_sql(tables)

        # find and rename column
        subcols.rename(str(self.arrow.right), str(self.arrow.left))

        # return sql statement
        return subquery, subcols

        # We replace the "real" attribute name later anyway,
        # so we do not need to change the sql statement here.
        # return f'SELECT DISTINCT {subcols.list} FROM ({subquery}) {self._name()}', subcols
