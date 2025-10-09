import sqlite3
from contextlib import closing
from typing import Dict, List, Tuple, Any

from ... import DatabaseError, Column, Constraint, ForeignKey, Table
from ...Connection import Connection as Base
from ...error import EmptyResultError


class Connection(Base):
    def __init__(self, path: str):
        self.path: str = path
        self.con: sqlite3.Connection = sqlite3.connect(path)
        self.con.execute('PRAGMA foreign_keys = ON')

    def close(self):
        self.con.close()

    def copy(self) -> 'Connection':
        return Connection(self.path)

    @staticmethod
    def multiple_statements_per_query() -> bool:
        return False

    def __str__(self) -> str:
        return f'SQLite: {self.path}'

    def execute(self, query: str) -> Tuple[List[str], List[List[Any]]]:
        with closing(self.con.cursor()) as cursor:
            try:
                cursor.execute(query)
            except Exception as e:
                if isinstance(e, sqlite3.Error):
                    # duckdb.OperationalError,
                    # duckdb.ProgrammingError,
                    # duckdb.InvalidInputException
                    text = str(e)
                    raise DatabaseError(text)
                else:
                    raise e

            # get rows
            rows = cursor.fetchall()

            # get columns
            if cursor.description is None:
                raise EmptyResultError()
            else:
                columns = [e[0] for e in cursor.description]

        return columns, rows

    def analyze(self) -> Dict[str, Table]:
        tables: Dict[str, Table] = {}
        constraints: Dict[int, Constraint] = {}

        with closing(self.con.cursor()) as cursor:
            # Get table names first. In the columns table we can not filter
            # for base tables and some of the tables might not be contained
            # in the constraints' information.
            for table_name, in self.con.execute('''
                        SELECT name
                        FROM sqlite_schema
                        WHERE type ='table' AND name NOT LIKE 'sqlite_%';
                    ''').fetchall():
                table = Table(table_name)
                tables[table.normalized_name] = table

            # Get column names and data types for each table.
            for table_name, table in tables.items():
                for column_name, data_type, not_null in self.con.execute(f'''
                    SELECT name, type, "notnull"
                    FROM pragma_table_info('{table_name}')
                '''):
                    column = Column(table, column_name, data_type, not_null == 0)
                    table.columns.append(column)

            # Find primary keys.
            for table_name, table in tables.items():
                for key_name, in self.con.execute(f'''
                    SELECT name
                    FROM pragma_index_list('{table_name}')
                    WHERE origin = 'pk'
                '''):
                    # get columns
                    constraint_columns = [c for c, in self.con.execute(f'''
                        SELECT name
                        FROM pragma_index_info('{key_name}')
                    ''')]

                    # store constraint
                    constraint_index = hash(key_name)

                    if constraint_index in constraints:
                        raise AssertionError(f'constraint with index {constraint_index} already stored')

                    constraint = Constraint(
                        constraint_index,
                        table,
                        tuple(table.get_column(c) for c in constraint_columns)
                    )
                    constraints[constraint_index] = constraint

                    # store key
                    if table.primary_key is not None:
                        raise AssertionError(f'discovered second primary key for table {table_name}')

                    table.primary_key = constraint

            # Find unique keys.
            for table_name, table in tables.items():
                for key_name, in self.con.execute(f'''
                    SELECT name
                    FROM pragma_index_list('{table_name}')
                    WHERE origin = 'u'
                '''):
                    # get columns
                    constraint_columns = [c for c, in self.con.execute(f'''
                        SELECT name
                        FROM pragma_index_info('{key_name}')
                    ''')]

                    # store constraint
                    constraint_index = hash(key_name)

                    if constraint_index in constraints:
                        raise AssertionError(f'constraint with index {constraint_index} already stored')

                    constraint = Constraint(
                        constraint_index,
                        table,
                        tuple(table.get_column(c) for c in constraint_columns)
                    )
                    constraints[constraint_index] = constraint

                    # store key
                    table.unique_keys.append(constraint)

            # Find foreign keys.
            for table_name, table in tables.items():
                current_id = None
                current_sources = []
                current_targets = []

                def store():
                    # create constraint
                    constraint_index = hash(f'{table_name}_fe_{current_id}')
                    constraint = Constraint(
                        constraint_index,
                        current_targets[0].table,
                        tuple(current_targets)
                    )

                    constraints[constraint_index] = constraint

                    # store key
                    key = ForeignKey(
                        tuple(current_sources),
                        constraint
                    )
                    table.foreign_keys.append(key)

                for id, from_col, to_table_name, to_col in self.con.execute(f'''
                    SELECT id, "from", "table", "to"
                    FROM pragma_foreign_key_list('{table_name}')
                    ORDER BY id
                '''):
                    # parse parameters as soon as id changes
                    if id != current_id:
                        # on the first run current_id is None
                        if current_id is not None:
                            store()

                        # reset current
                        current_id = id
                        current_sources = []
                        current_targets = []

                    # add columns to parse later
                    normalized_to_table_name = Table.normalize_name(to_table_name)

                    current_sources.append(table.get_column(from_col))
                    current_targets.append(tables[normalized_to_table_name].get_column(to_col))

                if len(current_sources) > 0:
                    store()

        # return result
        return tables
