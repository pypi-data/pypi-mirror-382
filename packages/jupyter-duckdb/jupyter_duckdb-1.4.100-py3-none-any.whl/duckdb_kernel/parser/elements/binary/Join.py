from typing import Tuple, Dict

from duckdb_kernel.db import Table
from ..RABinaryOperator import RABinaryOperator
from ...util.RenamableColumnList import RenamableColumnList


class Join(RABinaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return chr(8904), chr(10781), 'join'

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subqueries
        lq, lcols = self.left.to_sql(tables)
        rq, rcols = self.right.to_sql(tables)

        # find matching columns
        join_cols, all_cols = lcols.intersect(rcols)

        on_clause = ' AND '.join(f'{l.current_name} = {r.current_name}' for l, r in join_cols)

        # create sql
        return f'SELECT {all_cols.list} FROM ({lq}) {self._name()} JOIN ({rq}) {self._name()} ON {on_clause}', all_cols
