import os
from typing import Dict, List, Tuple

from duckdb_kernel.db import Connection as DB, Table
from duckdb_kernel.db.error import EmptyResultError
from duckdb_kernel.parser.elements import RAElement
from duckdb_kernel.parser.elements.binary import ConditionalSet

with open('examples/tables.sql', 'r', encoding='utf-8') as file:
    EXAMPLE_STMTS = [stmt
                     for stmt in file.read().split(';')
                     if stmt.strip()]


class Connection:
    def __enter__(self):
        db_type = os.environ.get('DB_TYPE')
        if db_type == 'postgres':
            host = os.environ.get('POSTGRES_HOST', 'localhost')
            port = int(os.environ.get('POSTGRES_PORT', 5432))
            username = os.environ.get('POSTGRES_USER', 'postgres')
            password = os.environ.get('POSTGRES_PASSWORD', 'postgres')

            from duckdb_kernel.db.implementation.postgres import Connection as PostgreSQL
            self.con: DB = PostgreSQL(host, port, username, password, None)
        elif db_type == 'sqlite':
            from duckdb_kernel.db.implementation.sqlite import Connection as SQLite
            self.con: DB = SQLite(':memory:')
        else:
            from duckdb_kernel.db.implementation.duckdb import Connection as DuckDB
            self.con: DB = DuckDB(':memory:')

        for stmt in EXAMPLE_STMTS:
            try:
                self.con.execute(stmt)
            except EmptyResultError:
                pass

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    @property
    def tables(self) -> Dict[str, Table]:
        return self.con.analyze()

    def execute_sql_return_cols(self, query: str) -> Tuple[List, List]:
        return self.con.execute(query)

    def execute_sql(self, query: str) -> List:
        _, rows = self.execute_sql_return_cols(query)
        return rows

    def execute_ra_return_cols(self, root: RAElement) -> Tuple[List, List]:
        sql = root.to_sql_with_renamed_columns(self.tables)
        cols, rows = self.execute_sql_return_cols(sql)

        return cols, sorted(rows, key=lambda t: tuple(-1 if x is None else x for x in t))

    def execute_ra(self, root: RAElement) -> List:
        _, rows = self.execute_ra_return_cols(root)
        return rows

    def execute_dc_return_cols(self, root: ConditionalSet) -> Tuple[List, List]:
        sql, cnm = root.to_sql_with_renamed_columns(self.tables)
        cols, rows = self.execute_sql_return_cols(sql)

        return [cnm.get(c, c) for c in cols], sorted(rows)

    def execute_dc(self, root: ConditionalSet) -> List:
        _, rows = self.execute_dc_return_cols(root)
        return rows


__all__ = ['Connection']
