from typing import Tuple, Dict

from duckdb_kernel.db import Table
from ..RABinaryOperator import RABinaryOperator
from ...util.RenamableColumnList import RenamableColumnList


class Division(RABinaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return '÷', ':'

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subqueries
        lq, lcols = self.left.to_sql(tables)
        rq, rcols = self.right.to_sql(tables)

        # difference and intersection preparation
        diff_cols = lcols.difference(rcols)
        diff_name = ', '.join(c.current_name for c in diff_cols)

        inter_cols, p = lcols.intersect(rcols)
        if len(inter_cols) == 0:
            raise AssertionError('divison can only be applied to relations with common columns')

        inter_name = ' AND '.join(f'{r.current_name} = {l.current_name}' for l, r in inter_cols)
        # inter_name_left = ', '.join(l.current_name for l, _ in inter_cols)
        inter_name_right = ', '.join(r.current_name for _, r in inter_cols)

        # create sql
        return f'''
            SELECT {diff_name}
            FROM ({lq}) {self._name()}
            WHERE EXISTS (
                SELECT {inter_name_right}
                FROM ({rq}) {self._name()}
                WHERE {inter_name}
            )
            GROUP BY {diff_name}
            HAVING COUNT(*) = (
                SELECT COUNT(*)
                FROM ({rq}) {self._name()}
            )
        ''', diff_cols
