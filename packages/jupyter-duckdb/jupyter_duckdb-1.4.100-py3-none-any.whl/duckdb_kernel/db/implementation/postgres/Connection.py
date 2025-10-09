import contextlib
import re
from typing import Tuple, List, Any, Optional, Dict
from uuid import uuid4

import psycopg

from .util import strip_delimiters
from ... import DatabaseError, Column, Constraint, ForeignKey, Table
from ...Connection import Connection as Base
from ...error import EmptyResultError


class Connection(Base):
    def __init__(self,
                 host: str, port: int,
                 username: Optional[str], password: Optional[str],
                 database_name: Optional[str]):
        self.host: str = host
        self.port: int = port
        self.username: Optional[str] = username
        self.password: Optional[str] = password

        options = {
            'host': host,
            'port': port,
            'user': username,
            'password': password,
            'autocommit': True
        }

        # If not database name is provided we create one.
        if database_name is None:
            # connect to the server without a database name
            with contextlib.closing(psycopg.connect(**options, dbname='postgres')) as temp_con:
                # create a database to use
                database_name: str = 'db_' + str(uuid4()).replace('-', '')
                temp_con.execute(f'CREATE DATABASE {database_name}')

        # Finally the "real" connection is created using the database name.
        self.con = psycopg.connect(**options, dbname=database_name)
        self.database_name: str = database_name

    def close(self):
        self.con.close()

    def copy(self) -> 'Connection':
        return Connection(self.host, self.port, self.username, self.password, self.database_name)

    def __str__(self) -> str:
        user = f'{self.username}@' if self.username is not None else ''
        return f'PostgreSQL: {user}{self.host}:{self.port}/{self.database_name}'

    def execute(self, query: str) -> Tuple[List[str], List[List[Any]]]:
        with self.con.cursor() as cursor:
            try:
                cursor.execute(query)
            except Exception as e:
                if isinstance(e, psycopg.Error):
                    text = str(e)
                    raise DatabaseError(text)
                else:
                    raise e

            # get rows
            try:
                rows = cursor.fetchall()
            except psycopg.ProgrammingError as e:
                text = str(e)
                if text.startswith((
                        "the last operation didn't produce a result",
                        "the last operation didn't produce records"
                )):
                    raise EmptyResultError()
                else:
                    raise e

            # get columns
            if cursor.description is None:
                columns = []
            else:
                columns = [e[0] for e in cursor.description]

        return columns, rows

    def analyze(self) -> Dict[str, Table]:
        tables: Dict[str, Table] = {}
        constraints: Dict[str, Constraint] = {}
        constraint_index: int = 0

        # First, receive the table names.
        for table_name, in self.con.execute('''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
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
        constraints_dict = {}

        for constraint_name, table_name, column_name in self.con.execute('''
            SELECT tc.constraint_name, tc.table_name, c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu
                USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c
                ON c.table_schema = tc.constraint_schema AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE tc.table_schema = 'public' AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY tc.table_name, c.ordinal_position
        '''):
            if constraint_name not in constraints_dict:
                constraints_dict[constraint_name] = (table_name, [])

            constraints_dict[constraint_name][1].append(column_name)

        for constraint_name, (table_name, column_names) in constraints_dict.items():
            # get table
            normalized_table_name = Table.normalize_name(table_name)

            if normalized_table_name not in tables:
                raise AssertionError(f'unknown table {table_name} for constraint {constraint_index}')

            table = tables[normalized_table_name]

            # store constraint
            constraint = Constraint(
                constraint_index,
                table,
                tuple(table.get_column(c) for c in column_names)
            )

            constraint_index += 1

            # store key
            if table.primary_key is not None:
                raise AssertionError(f'discovered second primary key for table {table_name}')

            table.primary_key = constraint

        # Find unqiue keys.
        constraints_dict = {}

        for constraint_name, table_name, column_name in self.con.execute('''
            SELECT tc.constraint_name, tc.table_name, c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu
                USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c
                ON c.table_schema = tc.constraint_schema AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE tc.table_schema = 'public' AND tc.constraint_type = 'UNIQUE'
            ORDER BY tc.table_name, c.ordinal_position
        '''):
            if constraint_name not in constraints_dict:
                constraints_dict[constraint_name] = (table_name, [])

            constraints_dict[constraint_name][1].append(column_name)

        for constraint_name, (table_name, column_names) in constraints_dict.items():
            # get table
            normalized_table_name = Table.normalize_name(table_name)

            if normalized_table_name not in tables:
                raise AssertionError(f'unknown table {table_name} for constraint {constraint_index}')

            table = tables[normalized_table_name]

            # store constraint
            constraint = Constraint(
                constraint_index,
                table,
                tuple(table.get_column(c) for c in column_names)
            )

            constraint_index += 1

            # store key
            table.unique_keys.append(constraint)

        # Find foreign keys.
        for source_table_name, fk_name, fk_def in self.con.execute('''
            SELECT conrelid::regclass, conname, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE contype = 'f'
            AND connamespace = 'public'::regnamespace
            ORDER BY conrelid::regclass::text, contype DESC
        '''):
            # extract information
            match = re.match(r'^FOREIGN KEY \((.*?)\) REFERENCES (.*?)\((.*?)\)', fk_def, re.IGNORECASE)
            if match is None:
                raise AssertionError(f'could not parse foreign key definitions for table {source_table_name}')

            source_table_name = strip_delimiters(source_table_name)
            normalized_source_table_name = Table.normalize_name(source_table_name)
            source_table_column_names = [strip_delimiters(c) for c in match.group(1).split(',')]

            target_table_name = strip_delimiters(match.group(2))
            normalized_target_table_name = Table.normalize_name(target_table_name)
            target_table_column_names = [strip_delimiters(c) for c in match.group(3).split(',')]

            # get tables
            if normalized_source_table_name not in tables:
                raise AssertionError(f'unknown table {source_table_name} for foreign key {fk_name}')

            source_table = tables[normalized_source_table_name]

            if normalized_target_table_name not in tables:
                raise AssertionError(f'unknown table {target_table_name} for foreign key {fk_name}')

            target_table = tables[normalized_target_table_name]

            # store constraint
            constraint = Constraint(
                constraint_index,
                target_table,
                tuple(target_table.get_column(c) for c in target_table_column_names)
            )

            constraint_index += 1

            # store key
            key = ForeignKey(tuple(source_table.get_column(c) for c in source_table_column_names), constraint)
            source_table.foreign_keys.append(key)

        # return result
        return tables
