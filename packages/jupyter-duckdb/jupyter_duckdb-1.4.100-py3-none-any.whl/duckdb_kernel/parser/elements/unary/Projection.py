from typing import Dict, Tuple

from duckdb_kernel.db import Table
from ..LogicElement import LogicElement
from ..LogicOperand import LogicOperand
from ..RAElement import RAElement
from ..RAUnaryOperator import RAUnaryOperator
from ...util.RenamableColumnList import RenamableColumnList


class Projection(RAUnaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return 'Π', 'π', 'pi'

    def __init__(self, target: RAElement, arg: LogicOperand):
        if not isinstance(arg, LogicOperand):
            raise AssertionError('only argument lists allowed as parameter')

        super().__init__(target)
        self.columns: LogicOperand = arg

    @property
    def arg(self) -> LogicElement:
        return self.columns

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subquery
        subquery, subcols = self.target.to_sql(tables)

        # map names to columns from subquery
        cols = subcols.filter(*self.columns)

        # get sql
        return f'SELECT DISTINCT {cols.list} FROM ({subquery}) {self._name()}', cols
