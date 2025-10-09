import pytest

from duckdb_kernel.db.error import EmptyResultError
from . import Connection


def test_simple_queries():
    query = 'SELECT Username FROM Users'

    with Connection() as con:
        assert con.execute_sql(query) == [
            ('Alice',),
            ('Bob',),
            ('Charlie',)
        ]


def test_empty_result():
    with Connection() as con:
        query = "SELECT Username FROM Users WHERE Username = 'abcdef'"
        assert con.execute_sql(query) == []

    with Connection() as con:
        query = 'CREATE TABLE foo (bar INTEGER PRIMARY KEY)'
        try:
            assert con.execute_sql(query) == []
        except EmptyResultError:
            pass


def test_empty_queries():
    for query in [
        '',
        ' ',
        '\n',
        '-- this is an empty query too'
    ]:
        with pytest.raises(EmptyResultError):
            with Connection() as con:
                con.execute_sql(query)

    with pytest.raises(Exception):
        with Connection() as con:
            query = '-- this is a query with syntax errors\nFOR foo IN bar'
            try:
                con.execute_sql(query)
            except EmptyResultError:
                pass
