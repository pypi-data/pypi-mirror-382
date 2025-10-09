from typing import Tuple, Dict

from duckdb_kernel.db import Table
from ..RABinaryOperator import RABinaryOperator
from ...util.RenamableColumnList import RenamableColumnList


class Difference(RABinaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '-', '\\'

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subqueries
        lq, lcols = self.left.to_sql(tables)
        rq, rcols = self.right.to_sql(tables)

        # check number of columns
        if len(lcols) != len(rcols):
            raise AssertionError('difference can only be applied to relations with the same number of columns')

        # create sql
        return f'{lq} EXCEPT {rq}', lcols
