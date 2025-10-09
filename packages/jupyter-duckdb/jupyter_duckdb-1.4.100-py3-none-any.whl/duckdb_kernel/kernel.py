import csv
import json
import math
import os
import re
import time
import traceback
from typing import Optional, Dict, List, Tuple

from ipykernel.kernelbase import Kernel

from .db import Connection, DatabaseError, Table
from .db.error import *
from .magics import *
from .parser import RAParser, DCParser, ParserError
from .util.ResultSetComparator import ResultSetComparator
from .util.SQL import SQL_KEYWORDS
from .util.TestError import TestError
from .util.formatting import row_count, rows_table, wrap_image
from .visualization import *


class DuckDBKernel(Kernel):
    DEFAULT_MAX_ROWS = 20

    implementation = 'DuckDB'
    implementation_version = '1.0'
    banner = 'DuckDB Kernel'
    language_info = {
        'name': 'duckdb',
        'mimetype': 'application/sql',
        'file_extension': '.sql',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # register magic commands
        self._magics: MagicCommandHandler = MagicCommandHandler()

        self._magics.add(
            MagicCommand('create').arg('database').opt('of').opt('name').on(self._create_magic),
            MagicCommand('load').arg('database').opt('name').on(self._load_magic),
            MagicCommand('copy').arg('source').arg('target').on(self._copy_magic),
            MagicCommand('use').arg('name').on(self._use_magic),
            MagicCommand('load_tests').arg('tests').on(self._load_tests_magic),
            MagicCommand('test').arg('name').result(True).on(self._test_magic),
            MagicCommand('all', 'all_rows').on(self._all_magic),
            MagicCommand('max_rows').arg('count').on(self._max_rows_magic),
            MagicCommand('query_max_rows').arg('count').on(self._query_max_rows_magic),
            MagicCommand('schema').flag('td').opt('only').on(self._schema_magic),
            MagicCommand('store').arg('file').flag('noheader').result(True).on(self._store_magic),
            MagicCommand('sql').disable('ra', 'dc', 'auto_parser'),
            MagicCommand('ra').disable('sql', 'dc', 'auto_parser').flag('analyze').code(True).on(self._ra_magic),
            MagicCommand('all_ra').arg('value', '1').on(self._all_ra_magic),
            MagicCommand('dc').disable('sql', 'ra', 'auto_parser').code(True).on(self._dc_magic),
            MagicCommand('all_dc').arg('value', '1').on(self._all_dc_magic),
            MagicCommand('auto_parser').disable('sql', 'ra', 'dc').code(True).on(self._auto_parser_magic),
            MagicCommand('guess_parser').arg('value', '1').on(self._guess_parser_magic),
            MagicCommand('plotly').arg('type').arg('mapping').opt('title').result(True).on(self._plotly_magic),
            MagicCommand('plotly_raw').opt('title').result(True).on(self._plotly_raw_magic)
        )

        # create placeholders for database and tests
        self._db: Dict[str, Connection] = {}
        self._tests: Dict = {}

    # output related functions
    def print(self, text: str, name: str = 'stdout'):
        self.send_response(self.iopub_socket, 'stream', {
            'name': name,
            'text': text
        })

    def print_exception(self, e: Exception):
        if isinstance(e, AssertionError):
            text = str(e)
        elif isinstance(e, MagicCommandException):
            text = str(e)
        elif isinstance(e, DatabaseError):
            text = str(e)

            # ignore InvalidInputException if an empty query was executed
            if text == 'Invalid Input Error: No open result set':
                return
        else:
            text = traceback.format_exc()

        self.print(text, 'stderr')

    def print_data(self, *data: str, mime: str = 'text/html'):
        for v in data:
            self.send_response(self.iopub_socket, 'display_data', {
                'data': {
                    mime: v
                },
                # `metadata` is required. Otherwise, Jupyter Lab does not display any output.
                # This is not the case when using Jupyter Notebook btw.
                'metadata': {}
            })

    # database related functions
    def _load_database(self, path: str, name: str) -> Connection:
        if name in self._db:
            raise ValueError(f'duplicate database name {name}')

        # If the provided path looks like a postgres url,
        # we want to use the postgres driver.
        if path.startswith(('postgresql://', 'postgres://', 'pgsql://', 'psql://', 'pg://')):
            # pull data from connection string
            re_expr = r'(postgresql|postgres|pgsql|psql|pg)://((.*?)(:(.*?))?@)?(.*?)(:(\d+))?(/(.*))?'
            match = re.fullmatch(re_expr, path)

            host = match.group(6)
            port = int(match.group(8)) if match.group(8) is not None else 5432
            username = match.group(3)
            password = match.group(5)
            database_name = match.group(10)

            # load and create instance
            from .db.implementation.postgres import Connection as Postgres
            self._db[name] = Postgres(host, port, username, password, database_name)

        # Otherwise the provided path is used to create an
        # in-process instance.
        else:
            # By default, we try to load DuckDB.
            try:
                from .db.implementation.duckdb import Connection as DuckDB
                self._db[name] = DuckDB(path)

            # If DuckDB is not installed or fails to load,
            # we use SQLite instead.
            except ImportError:
                self.print('DuckDB is not available\n')

                from .db.implementation.sqlite import Connection as SQLite
                self._db[name] = SQLite(path)

        return self._db[name]

    def _unload_database(self, name: str):
        if name in self._db:
            self._db[name].close()
            del self._db[name]

            return True
        else:
            return False

    def _execute_stmt(self, silent: bool, state: MagicState, name: str, query: str) \
            -> Tuple[Optional[List[str]], Optional[List[List]]]:
        if state.db is None:
            raise AssertionError('load a database first')

        # execute query and store start and end timestamp
        st = time.time()

        try:
            columns, rows = state.db.execute(query)
        except EmptyResultError:
            columns, rows = None, None

        et = time.time()

        # print result if not silent
        if not silent:
            # print EXPLAIN queries as raw text if using DuckDB
            if query.strip().startswith('EXPLAIN') and state.db.plain_explain():
                for ekey, evalue in rows:
                    html = f'<b>{ekey}</b><br><pre>{evalue}</pre>'
                    break
                else:
                    html = ''

            # print every other query as a table
            else:
                if columns is not None:
                    # table header
                    mapped_columns = (state.column_name_mapping.get(c, c) for c in columns)
                    table_header = ''.join(f'<th>{c}</th>' for c in mapped_columns)

                    # table data
                    if state.max_rows is not None and len(rows) > state.max_rows:
                        table_data = f'''
                            {rows_table(rows[:math.ceil(state.max_rows / 2)])}
                            <tr>
                                <td colspan="{len(columns)}" 
                                    style="text-align: center"
                                    title="{row_count(len(rows) - state.max_rows)} omitted">
                                    ...
                                </td>
                            </tr>
                            {rows_table(rows[-math.floor(state.max_rows // 2):])}
                        '''
                    else:
                        table_data = rows_table(rows)

                    # send to client
                    html = (f'''
                        <table class="duckdb-query-result-table">
                            {table_header}
                            {table_data}
                        </table>
                        
                        {row_count(len(rows))} in {et - st:.3f}s
                    ''')

                else:
                    html = f'statement executed without result in {et - st:.3f}s'

            self.print_data(f'''
                <div class="duckdb-query-result {name}">
                    {html}
                </div>
            ''')

        return columns, rows

    # magic command related functions
    def _create_magic(self, silent: bool, state: MagicState,
                      path: str, of: Optional[str], name: Optional[str]):
        self._load(silent, state, path, True, of, name)

    def _load_magic(self, silent: bool, state: MagicState,
                    path: str, name: Optional[str]):
        self._load(silent, state, path, False, None, name)

    def _load(self, silent: bool, state: MagicState,
              path: str, create: bool, of: Optional[str], name: Optional[str]):
        # use default name if non provided
        if name is None:
            name = 'default'

        if not silent:
            self.print(f'--- connection {name} ---\n')

        # unload current database if necessary
        if self._unload_database(name):
            if not silent:
                self.print('unloaded database\n')

        # No user cares about the kernel version,
        # so I removed the printing.

        # clean path
        if path.startswith(("'", '"')):
            path = path[1:]
        if path.endswith(("'", '"')):
            path = path[:-1]

        # load new database
        if create and os.path.exists(path):
            os.remove(path)

        state.db = self._load_database(path, name)
        if not silent:
            # self.print(f'loaded database "{path}"\n')
            self.print(str(state.db) + '\n')

        # copy data from source database
        if of is not None:
            # clean path
            if of.startswith(("'", '"')):
                of = of[1:]
            if of.endswith(("'", '"')):
                of = of[:-1]

            # load sql files
            if of.endswith('.sql'):
                with open(of, 'r', encoding='utf-8') as file:
                    content = file.read()

                    # You can only execute one statement at a time using SQLite.
                    if not state.db.multiple_statements_per_query():
                        statements = re.split(r';\r?\n', content)
                        for statement in statements:
                            try:
                                state.db.execute(statement)
                            except EmptyResultError:
                                pass

                    # Other DBMS can execute multiple statements at a time.
                    else:
                        try:
                            state.db.execute(content)
                        except EmptyResultError:
                            pass

                    if not silent:
                        self.print(f'executed "{of}"\n')

            # load database files
            else:
                import duckdb
                with duckdb.connect(of, read_only=True) as of_db:
                    of_db.execute('SHOW TABLES')
                    for table, in of_db.fetchall():
                        transfer_df = of_db.query(f'SELECT * FROM {table}').to_df()
                        state.db.execute(f'CREATE TABLE {table} AS SELECT * FROM transfer_df')

                        if not silent:
                            self.print(f'transferred table {table}\n')

    def _copy_magic(self, silent: bool, state: MagicState, source: str, target: str):
        if source not in self._db:
            raise ValueError(f'unknown connection {source}')

        if not silent:
            self.print(f'--- connection {target} ---\n')

        # unload current database if necessary
        if self._unload_database(target):
            if not silent:
                self.print('unloaded database\n')

        # copy connection
        self._db[target] = self._db[source].copy()
        state.db = self._db[target]

        if not silent:
            self.print(str(state.db) + '\n')

    def _use_magic(self, silent: bool, state: MagicState, name: str):
        if name not in self._db:
            raise ValueError(f'unknown connection {name}')

        state.db = self._db[name]

    def _load_tests_magic(self, silent: bool, state: MagicState, tests: str):
        with open(tests, 'r', encoding='utf-8') as tests_file:
            self._tests = json.load(tests_file)
            for test in self._tests.values():
                if 'attributes' in test:
                    rows = {k: [] for k in test['attributes']}
                    for row in test['equals']:
                        for k, v in zip(test['attributes'], row):
                            rows[k].append(v)

                    test['equals'] = rows

            self.print(f'loaded tests from {tests}\n')

    def _test_magic(self, silent: bool, state: MagicState, result_columns: List[str], result: List[List], name: str):
        # If the query was empty, result_columns and result may be None.
        if result_columns is None or result is None:
            self.print_data(wrap_image(False, 'Statement did not return data.'))
            return

        # Testing makes no sense if there is no output.
        if silent:
            return

        # store result_columns without table names
        result_columns = [col.rsplit('.', 1)[-1] for col in result_columns]

        # extract data for test
        test_data = self._tests[name]

        # execute test
        try:
            self._execute_test(test_data, result_columns, result)
            self.print_data(wrap_image(True))
        except TestError as e:
            self.print_data(wrap_image(False, e.message))
            if os.environ.get('DUCKDB_TESTS_RAISE_EXCEPTION', 'false').lower() in ('true', '1'):
                raise e

    @staticmethod
    def _execute_test(test_data: Dict, result_columns: List[str], result: List[List]):
        # check columns if required
        if isinstance(test_data['equals'], dict):
            # get column order
            data_columns = list(test_data['equals'].keys())
            column_order = []

            for dc in data_columns:
                found = 0
                for i, rc in enumerate(result_columns):
                    if dc.lower() == rc.lower():
                        column_order.append(i)
                        found += 1

                if found == 0:
                    raise TestError(f'attribute {dc} missing')
                if found >= 2:
                    raise TestError(f'ambiguous attribute {dc}')

            # abort if columns from result are unnecessary
            for i, rc in enumerate(result_columns):
                if i not in column_order:
                    raise TestError(f'unnecessary attribute {rc}')

            # reorder columns and transform to list of lists
            sorted_columns = [x for _, x in sorted(zip(column_order, data_columns))]
            rows = []

            for row in zip(*(test_data['equals'][col] for col in sorted_columns)):
                rows.append(row)

        else:
            rows = test_data['equals']

        # ordered test
        if test_data['ordered']:
            # calculate diff
            rsc = ResultSetComparator(result, rows)

            missing = len(rsc.ordered_right_only)
            if missing > 0:
                raise TestError(f'{row_count(missing)} missing')

            missing = len(rsc.ordered_left_only)
            if missing > 0:
                raise TestError(f'{row_count(missing)} more than required')

        # unordered test
        else:
            # calculate diff
            rsc = ResultSetComparator(result, rows)

            below = len(rsc.right_only)
            above = len(rsc.left_only)

            # print result
            if below > 0 and above > 0:
                raise TestError(f'{row_count(below)} missing, {row_count(above)} unnecessary')
            elif below > 0:
                raise TestError(f'{row_count(below)} missing')
            elif above > 0:
                raise TestError(f'{row_count(above)} unnecessary')

    def _all_magic(self, silent: bool, state: MagicState):
        state.max_rows = None

    def _max_rows_magic(self, silent: bool, state: MagicState, count: str):
        if count.lower() != 'none':
            DuckDBKernel.DEFAULT_MAX_ROWS = int(count)
        else:
            DuckDBKernel.DEFAULT_MAX_ROWS = None

        state.max_rows = DuckDBKernel.DEFAULT_MAX_ROWS

    def _query_max_rows_magic(self, silent: bool, state: MagicState, count: str):
        state.max_rows = int(count) if count.lower() != 'none' else None

    def _schema_magic(self, silent: bool, state: MagicState, td: bool, only: Optional[str]):
        if silent:
            return

        if state.db is None:
            raise AssertionError('load a database first')

        # analyze tables
        tables = state.db.analyze()

        # apply filter
        if only is None:
            table_values = list(tables.values())

        else:
            whitelist = set()

            # split and strip names
            names = [Table.normalize_name(n.strip()) for n in re.split(r'[, \t]', only)]

            # add initial tables to result set
            for name in names:
                if name not in tables:
                    raise AssertionError(f'table {name} not found')
                whitelist.add(tables[name])

            # iterate until the result set does not change
            last_size = 0
            while last_size < len(whitelist):
                last_size = len(whitelist)

                # everything a foreign key reaches from this group
                for rel in list(whitelist):
                    for fe in rel.foreign_keys:
                        whitelist.add(fe.constraint.table)

                # everything that is reachable using a foreign key
                for rel in tables.values():
                    for fe in rel.foreign_keys:
                        if fe.constraint.table in whitelist:
                            whitelist.add(rel)

            table_values = list(whitelist)

        # create and show visualization
        vd = SchemaDrawer(table_values)
        svg = vd.to_svg(not td)

        self.print_data(svg)

    def _store_magic(self, silent: bool, state: MagicState,
                     result_columns: List[str], result: List[List],
                     file: str, noheader: bool):
        _, ext = file.rsplit('.', 1)

        # csv
        if ext == 'csv':
            with open(file, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)

                if not noheader:
                    writer.writerow(result_columns)

                for row in result:
                    writer.writerow(row)

            self.print(f'result stored to {file}', name='stderr')

        # unsupported
        else:
            raise ValueError(f'extension {ext} not supported')

    def _ra_magic(self, silent: bool, state: MagicState, analyze: bool):
        if silent:
            return

        if not state.code.strip():
            return

        if state.db is None:
            raise AssertionError('load a database first')

        # analyze tables
        tables = state.db.analyze()

        # parse ra input
        root_node = RAParser.parse_query(state.code)

        # create and show visualization
        if analyze:
            vd = RATreeDrawer(state.db, root_node, tables)

            svg = vd.to_interactive_svg()
            self.print_data(svg)

            state.code = {
                node_id: node.to_sql_with_renamed_columns(tables)
                for node_id, node in vd.nodes.items()
            }

        else:
            state.code = root_node.to_sql_with_renamed_columns(tables)

    def _all_ra_magic(self, silent: bool, state: MagicState, value: str):
        if value.lower() in ('1', 'on', 'true'):
            self._magics['ra'].default(True)
            self._magics['dc'].default(False)

            self.print('All further cells are interpreted as %RA.\n')
        else:
            self._magics['ra'].default(False)

    def _dc_magic(self, silent: bool, state: MagicState):
        if silent:
            return

        if not state.code.strip():
            return

        if state.db is None:
            raise AssertionError('load a database first')

        # analyze tables
        tables = state.db.analyze()

        # parse dc input
        root_node = DCParser.parse_query(state.code)

        # generate sql
        sql, cnm = root_node.to_sql_with_renamed_columns(tables)

        state.code = sql
        state.column_name_mapping.update(cnm)

    def _all_dc_magic(self, silent: bool, state: MagicState, value: str):
        if value.lower() in ('1', 'on', 'true'):
            self._magics['dc'].default(True)
            self._magics['ra'].default(False)

            self.print('All further cells are interpreted as %DC.\n')
        else:
            self._magics['dc'].default(False)

    def _guess_parser_magic(self, silent: bool, state: MagicState, value: str):
        if value.lower() in ('1', 'on', 'true'):
            self._magics['auto_parser'].default(True)
            self.print('The correct parser is guessed for each subsequently executed cell.\n')
        else:
            self._magics['auto_parser'].default(False)

    def _auto_parser_magic(self, silent: bool, state: MagicState):
        # do not handle statements starting with SQL keywords
        first_word = state.code.strip().split(maxsplit=1)
        if len(first_word) > 0:
            if first_word[0].upper() in SQL_KEYWORDS:
                return

        # try to parse DC
        try:
            self._dc_magic(silent, state)
            return
        except ParserError as e:
            if e.depth > 0:
                raise e

        # try to parse RA
        try:
            self._ra_magic(silent, state, analyze=False)
            return
        except ParserError as e:
            if e.depth > 0:
                raise e

    def _plotly_magic(self, silent: bool, state: MagicState,
                      cols: List, rows: List[Tuple],
                      type: str, mapping: str, title: str = None):
        # split mapping and handle asterisks
        mapping = [m.strip() for m in mapping.split(',')]

        for i in range(len(mapping)):
            if mapping[i] == '*':
                mapping = mapping[:i] + cols + mapping[i + 1:]

        # convert all column names to lower case
        lower_cols = [c.lower() for c in cols]
        lower_mapping = [m.lower() for m in mapping]

        # map desired columns to indices
        mapped_indices = {}
        for ok, lk in zip(mapping, lower_mapping):
            for i in range(len(lower_cols)):
                if lk == lower_cols[i]:
                    mapped_indices[ok] = i
                    break
            else:
                raise ValueError(f'unknown column {ok}')

        # map desired columns to value lists
        mapped_values = {
            m: [r[i] for r in rows]
            for m, i in mapped_indices.items()
        }
        mapped_keys = iter(mapped_values.keys())

        # get required chart type
        match type.lower():
            case 'scatter':
                if len(lower_mapping) < 2: raise ValueError('scatter requires at least x and y values')
                html = draw_scatter_chart(title,
                                          mapped_values[next(mapped_keys)],
                                          **{k: mapped_values[k] for k in mapped_keys})
            case 'line':
                if len(lower_mapping) < 2: raise ValueError('lines requires at least x and y values')
                html = draw_line_chart(title,
                                       mapped_values[next(mapped_keys)],
                                       **{k: mapped_values[k] for k in mapped_keys})

            case 'bar':
                if len(lower_mapping) < 2: raise ValueError('bar requires at least x and y values')
                html = draw_bar_chart(title,
                                      mapped_values[next(mapped_keys)],
                                      **{k: mapped_values[k] for k in mapped_keys})

            case 'pie':
                if len(lower_mapping) != 2: raise ValueError('pie requires labels and values')
                html = draw_pie_chart(title,
                                      mapped_values[next(mapped_keys)],
                                      mapped_values[next(mapped_keys)])

            case 'bubble':
                if len(lower_mapping) != 4: raise ValueError('bubble requires x, y, size and color')
                html = draw_bubble_chart(title,
                                         mapped_values[next(mapped_keys)],
                                         mapped_values[next(mapped_keys)],
                                         mapped_values[next(mapped_keys)],
                                         mapped_values[next(mapped_keys)])

            case 'heatmap':
                if len(lower_mapping) != 3: raise ValueError('heatmap requires x, y and z values')
                html = draw_heatmap_chart(title,
                                          mapped_values[next(mapped_keys)],
                                          mapped_values[next(mapped_keys)],
                                          mapped_values[next(mapped_keys)])

            case _:
                raise ValueError(f'unknown type: {type}')

        # finally print the code
        self.print_data(html, mime='text/html')

    def _plotly_raw_magic(self, silent: bool, state: MagicState,
                          cols: List, rows: List[Tuple],
                          title: str = None):
        if len(cols) != 1 and len(rows) != 1:
            raise ValueError(f'expected exactly one column and one row')

        self.print_data(
            draw_chart(title, rows[0][0]),
            mime='text/html'
        )

    # jupyter related functions
    def do_execute(self, code: str, silent: bool,
                   store_history: bool = True, user_expressions: dict = None, allow_stdin: bool = False,
                   **kwargs):
        try:
            # get magic command
            if len(self._db) > 0:
                init_db = self._db[list(self._db.keys())[0]]
            else:
                init_db = None

            magic_state = MagicState(init_db, code, DuckDBKernel.DEFAULT_MAX_ROWS)
            pre_query_callbacks, post_query_callbacks = self._magics(silent, magic_state)

            # execute magic commands here if it does not depend on query results
            for callback in pre_query_callbacks:
                callback()

            # execute statement if needed
            cols, rows = None, None

            if not isinstance(magic_state.code, dict):
                magic_state.code = {'default': magic_state.code}

            for name, code in reversed(magic_state.code.items()):
                if code.strip():
                    cols, rows = self._execute_stmt(silent, magic_state, name, code)

            # execute magic command here if it does depend on query results
            for callback in post_query_callbacks:
                callback(cols, rows)

            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}
            }

        except Exception as e:
            self.print_exception(e)

            return {
                'status': 'error',
                'ename': str(type(e)),
                'evalue': str(e),
                'traceback': traceback.format_exc()
            }

    def do_shutdown(self, restart):
        for name in list(self._db.keys()):
            self._unload_database(name)

        return super().do_shutdown(restart)
