from typing import Dict, List, Tuple, Any

import duckdb

from ... import DatabaseError, Column, Constraint, ForeignKey, Table
from ...Connection import Connection as Base
from ...error import EmptyResultError


class Connection(Base):
    def __init__(self, path: str):
        self.path: str = path
        self.con: duckdb.DuckDBPyConnection = duckdb.connect(path, read_only=False)

    def close(self):
        self.con.close()

    def copy(self) -> 'Connection':
        return Connection(self.path)

    @staticmethod
    def plain_explain() -> bool:
        return True

    def __str__(self) -> str:
        return f'DuckDB: {self.path}'

    def execute(self, query: str) -> Tuple[List[str], List[List[Any]]]:
        with self.con.cursor() as cursor:
            try:
                cursor.execute(query)
            except Exception as e:
                if isinstance(e, duckdb.Error):
                    # duckdb.OperationalError,
                    # duckdb.ProgrammingError,
                    # duckdb.InvalidInputException
                    text = str(e)
                    raise DatabaseError(text)
                else:
                    raise e

            # get rows
            try:
                rows = cursor.fetchall()
            except duckdb.InvalidInputException as e:
                raise EmptyResultError(str(e))

            # get columns
            if cursor.description is None:
                columns = []
            else:
                columns = [e[0] for e in cursor.description]

        return columns, rows

    def analyze(self) -> Dict[str, Table]:
        tables: Dict[str, Table] = {}
        constraints: Dict[Tuple, Constraint] = {}

        # Get table names first. In the columns table we can not filter
        # for base tables and some of the tables might not be contained
        # in the constraints' information.
        for table_name, in self.con.execute('''
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_type == 'BASE TABLE'
                ''').fetchall():
            table = Table(table_name)
            tables[table.normalized_name] = table

        # Get column names and data types for each table.
        for table_name, column_name, data_type, is_nullable in self.con.execute('''
                    SELECT
                        table_name,
                        column_name,
                        data_type,
                        is_nullable
                    FROM information_schema.columns
                    ORDER BY ordinal_position ASC
                ''').fetchall():
            normalized_table_name = Table.normalize_name(table_name)
            if normalized_table_name in tables:
                table = tables[normalized_table_name]

                column = Column(table, column_name, data_type, is_nullable == 'YES')
                table.columns.append(column)

        # Find primary keys.
        for table_name, constraint_index, constraint_columns in self.con.execute('''
                    SELECT
                        table_name,
                        constraint_index,
                        constraint_column_names
                    FROM duckdb_constraints()
                    WHERE constraint_type = 'PRIMARY KEY'
                    ORDER BY constraint_index ASC
                ''').fetchall():
            # get table
            normalized_table_name = Table.normalize_name(table_name)

            if normalized_table_name not in tables:
                raise AssertionError(f'unknown table {table_name} for constraint {constraint_index}')

            table = tables[normalized_table_name]

            # store constraint
            if constraint_index in constraints:
                raise AssertionError(f'constraint with index {constraint_index} already stored')

            constraint = Constraint(
                constraint_index,
                table,
                tuple(table.get_column(c) for c in constraint_columns)
            )
            constraints[(normalized_table_name, *constraint_columns)] = constraint

            # store key
            if table.primary_key is not None:
                raise AssertionError(f'discovered second primary key for table {table_name}')

            table.primary_key = constraint

        # Find unique keys.
        for table_name, constraint_index, constraint_columns in self.con.execute('''
                    SELECT
                        table_name,
                        constraint_index,
                        constraint_column_names
                    FROM duckdb_constraints()
                    WHERE constraint_type = 'UNIQUE'
                    ORDER BY constraint_index ASC
                ''').fetchall():
            # get table
            normalized_table_name = Table.normalize_name(table_name)

            if normalized_table_name not in tables:
                raise AssertionError(f'unknown table {table_name} for constraint {constraint_index}')

            table = tables[normalized_table_name]

            # store constraint
            if constraint_index in constraints:
                raise AssertionError(f'constraint with index {constraint_index} already stored')

            constraint = Constraint(
                constraint_index,
                table,
                tuple(table.get_column(c) for c in constraint_columns)
            )
            constraints[(normalized_table_name, *constraint_columns)] = constraint

            # store key
            table.unique_keys.append(constraint)

        # Find foreign keys.
        for table_name, constraint_index, constraint_columns, referenced_table, referenced_column_names, in self.con.execute('''
                    SELECT
                        table_name,
                        constraint_index,
                        constraint_column_names,
                        referenced_table,
                        referenced_column_names
                    FROM duckdb_constraints()
                    WHERE constraint_type = 'FOREIGN KEY'
                    ORDER BY constraint_index ASC
                ''').fetchall():
            # get table
            normalized_table_name = Table.normalize_name(table_name)

            if normalized_table_name not in tables:
                raise AssertionError(f'unknown table {table_name} for constraint {constraint_index}')

            table = tables[normalized_table_name]

            # lookup constraint
            constraint_key = (Table.normalize_name(referenced_table), *referenced_column_names)
            if constraint_key not in constraints:
                raise AssertionError(f'constraint with key {constraint_key} not discovered previously')

            constraint = constraints[constraint_key]

            # store key
            key = ForeignKey(tuple(table.get_column(c) for c in constraint_columns), constraint)
            table.foreign_keys.append(key)

        # return result
        return tables
