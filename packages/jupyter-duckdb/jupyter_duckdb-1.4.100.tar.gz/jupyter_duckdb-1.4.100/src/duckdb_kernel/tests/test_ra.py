import pytest

import duckdb_kernel.parser.elements.binary as BinaryOperators
import duckdb_kernel.parser.elements.unary as UnaryOperators
from duckdb_kernel.parser import RAParser, RAParserError
from duckdb_kernel.parser.elements import RAOperand, LogicElement
from . import Connection


def test_case_insensitivity():
    for query in (
            'Users',
            'users',
            'USERS',
            'userS'
    ):
        root = RAParser.parse_query(query)

        # root is an RAOperand
        assert isinstance(root, RAOperand)

        # Root's name is the relation name in whatever case
        # it has been written.
        assert root.name == query

        # execute to test case insensitivity
        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (1, 'Alice'),
                (2, 'Bob'),
                (3, 'Charlie')
            ]

    for query in (
            'π [ Username ] ( Users )',
            'π [ username ] ( Users )',
            'π [ userName ] ( Users )'
    ):
        root = RAParser.parse_query(query)

        # execute to test case insensitivity
        with (Connection() as con):
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'username'
            ]
            assert rows == [
                ('Alice',),
                ('Bob',),
                ('Charlie',)
            ]

    for query in (
            'π [ Id, Username ] ( Users )',
            'π [ id, username ] ( Users )',
            'π [ iD, userName ] ( Users )'
    ):
        root = RAParser.parse_query(query)

        # execute to test case insensitivity
        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (1, 'Alice'),
                (2, 'Bob'),
                (3, 'Charlie')
            ]


def test_binary_operator_cross():
    for query in (
            r'Shows x Seasons',
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.Cross)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Shows'
        assert isinstance(root.right, RAOperand) and root.right.name == 'Seasons'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'shows.showid',
                'shows.showname',
                'seasons.seasonnumber',
                'seasons.showid',
                'seasons.seasonname'
            ]
            assert rows == [
                (1, 'Show 1', 1, 1, 'Show 1 / Season 1'),
                (1, 'Show 1', 1, 2, 'Show 2 / Season 1'),
                (1, 'Show 1', 2, 1, 'Show 1 / Season 2'),
                (1, 'Show 1', 2, 2, 'Show 2 / Season 2'),
                (2, 'Show 2', 1, 1, 'Show 1 / Season 1'),
                (2, 'Show 2', 1, 2, 'Show 2 / Season 1'),
                (2, 'Show 2', 2, 1, 'Show 1 / Season 2'),
                (2, 'Show 2', 2, 2, 'Show 2 / Season 2')
            ]


def test_binary_operator_difference():
    for query in (
            r'Users - BannedUsers',
            r'Users \ BannedUsers',
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.Difference)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Users'
        assert isinstance(root.right, RAOperand) and root.right.name == 'BannedUsers'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (1, 'Alice'),
                (3, 'Charlie')
            ]


def test_binary_operator_division():
    for query in (
            r'π [ShowId, SeasonNumber, EpisodeNumber] (Episodes) ÷ π [ EpisodeNumber ] (σ [ ShowId = 1 AND SeasonNumber = 1 ] (Episodes))',
            r'π [ShowId, SeasonNumber, EpisodeNumber] (Episodes) : π [ EpisodeNumber ] (σ [ ShowId = 1 AND SeasonNumber = 1 ] (Episodes))',
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.Division)
        assert isinstance(root.left, UnaryOperators.Projection)
        assert isinstance(root.left.target, RAOperand) and root.left.target.name == 'Episodes'
        assert isinstance(root.right, UnaryOperators.Projection)
        assert isinstance(root.right.target, UnaryOperators.Selection)
        assert isinstance(root.right.target.target, RAOperand) and root.right.target.target.name == 'Episodes'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'showid',
                'seasonnumber'
            ]
            assert rows == [
                (1, 1),
                (1, 2)
            ]


def test_binary_operator_intersection():
    for query in (
            r'Users ∩ BannedUsers',
            r'Users cap BannedUsers'
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.Intersection)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Users'
        assert isinstance(root.right, RAOperand) and root.right.name == 'BannedUsers'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (2, 'Bob')
            ]


def test_binary_operator_join():
    for query in (
            r'Shows ⋈ Seasons',
            r'Shows join Seasons'
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.Join)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Shows'
        assert isinstance(root.right, RAOperand) and root.right.name == 'Seasons'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'shows.showid',
                'shows.showname',
                'seasons.seasonnumber',
                'seasons.seasonname'
            ]
            assert rows == [
                (1, 'Show 1', 1, 'Show 1 / Season 1'),
                (1, 'Show 1', 2, 'Show 1 / Season 2'),
                (2, 'Show 2', 1, 'Show 2 / Season 1'),
                (2, 'Show 2', 2, 'Show 2 / Season 2')
            ]


def test_binary_operator_ljoin():
    for query in (
            r'Users ⟕ BannedUsers',
            r'Users ljoin BannedUsers'
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.LeftOuterJoin)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Users'
        assert isinstance(root.right, RAOperand) and root.right.name == 'BannedUsers'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'users.id',
                'users.username',
                'bannedusers.bannedusername'
            ]
            assert rows == [
                (1, 'Alice', None),
                (2, 'Bob', 'Bob'),
                (3, 'Charlie', None),
            ]


def test_binary_operator_rjoin():
    for query in (
            r'Users ⟖ BannedUsers',
            r'Users rjoin BannedUsers'
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.RightOuterJoin)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Users'
        assert isinstance(root.right, RAOperand) and root.right.name == 'BannedUsers'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'bannedusers.id',
                'users.username',
                'bannedusers.bannedusername'
            ]
            assert rows == [
                (2, 'Bob', 'Bob'),
                (4, None, 'David')
            ]


def test_binary_operator_fjoin():
    for query in (
            r'Users ⟗ BannedUsers',
            r'Users fjoin BannedUsers',
            r'Users ojoin BannedUsers'
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.FullOuterJoin)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Users'
        assert isinstance(root.right, RAOperand) and root.right.name == 'BannedUsers'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'users.id',
                'users.username',
                'bannedusers.bannedusername'
            ]
            assert rows == [
                (1, 'Alice', None),
                (2, 'Bob', 'Bob'),
                (3, 'Charlie', None),
                (4, None, 'David')
            ]


def test_binary_operator_union():
    for query in (
            r'Users ∪ BannedUsers',
            r'Users cup BannedUsers'
    ):
        root = RAParser.parse_query(query)

        assert isinstance(root, BinaryOperators.Union)
        assert isinstance(root.left, RAOperand) and root.left.name == 'Users'
        assert isinstance(root.right, RAOperand) and root.right.name == 'BannedUsers'

        with Connection() as con:
            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (1, 'Alice'),
                (2, 'Bob'),
                (3, 'Charlie'),
                (4, 'David')
            ]


def test_unary_operator_projection():
    with Connection() as con:
        for query in (
                r'π Id Users',
                r'π [ Id ] Users',
                r'π [ Id ] ( Users )',
                r'π[Id](Users)',
                r'Pi Id Users',
                r'Pi [ Id ] Users',
                r'Pi [ Id ] ( Users )',
                r'Pi[Id](Users)'
        ):
            root = RAParser.parse_query(query)

            assert isinstance(root, UnaryOperators.Projection)
            assert isinstance(root.arg, LogicElement)
            assert isinstance(root.target, RAOperand) and root.target.name == 'Users'

            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id'
            ]
            assert rows == [
                (1,),
                (2,),
                (3,)
            ]

        for query in (
                r'π Id π Id, Username Users',
                r'π [ Id ] (π [ Id, Username ] (Users))',
                r'π[Id]π[Id,Username]Users',
                r'Pi Id Pi Id, Username Users',
                r'Pi [ Id ] (Pi [ Id, Username ] (Users))',
                r'Pi[Id]Pi[Id,Username]Users'
        ):
            root = RAParser.parse_query(query)

            assert isinstance(root, UnaryOperators.Projection)
            assert isinstance(root.arg, LogicElement)
            assert isinstance(root.target, UnaryOperators.Projection)
            assert isinstance(root.target.arg, LogicElement)
            assert isinstance(root.target.target, RAOperand) and root.target.target.name == 'Users'

            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id'
            ]
            assert rows == [
                (1,),
                (2,),
                (3,)
            ]


def test_unary_operator_rename():
    with Connection() as con:
        for query in (
                r'β Id2 ← Id Users',
                r'β [ Id2 ← Id ] Users',
                r'β [ Id2 ← Id ] ( Users )',
                r'β[Id2←Id](Users)',
                r'Beta Id2 ← Id Users',
                r'Beta [ Id2 ← Id ] Users',
                r'Beta [ Id2 ← Id ] ( Users )',
                r'Beta[Id2←Id](Users)',
                r'Beta Id2 <- Id Users',
                r'Beta [ Id2 <- Id ] Users',
                r'Beta [ Id2 <- Id ] ( Users )',
                r'Beta[Id2<-Id](Users)'
        ):
            root = RAParser.parse_query(query)

            assert isinstance(root, UnaryOperators.Rename)
            assert isinstance(root.arg, LogicElement)
            assert isinstance(root.target, RAOperand) and root.target.name == 'Users'

            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id2',
                'username'
            ]
            assert rows == [
                (1, 'Alice'),
                (2, 'Bob'),
                (3, 'Charlie')
            ]

        for query in (
                r'β Id ← Id2 β Id2 ← Id Users',
                r'β [Id ← Id2] (β [Id2 ← Id] (Users))',
                r'βId←Id2βId2←Id Users',
                r'beta Id ← Id2 beta Id2 ← Id Users',
                r'beta [Id ← Id2] (beta [Id2 ← Id] (Users))',
                r'beta Id←Id2 beta Id2←Id Users',
                r'beta Id <- Id2 beta Id2 <- Id Users',
                r'beta [Id <- Id2] (beta [Id2 <- Id] (Users))',
                r'beta Id<-Id2 beta Id2<-Id Users'
        ):
            root = RAParser.parse_query(query)

            assert isinstance(root, UnaryOperators.Rename)
            assert isinstance(root.arg, LogicElement)
            assert isinstance(root.target, UnaryOperators.Rename)
            assert isinstance(root.target.arg, LogicElement)
            assert isinstance(root.target.target, RAOperand) and root.target.target.name == 'Users'

            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (1, 'Alice'),
                (2, 'Bob'),
                (3, 'Charlie')
            ]


def test_unary_operator_selection():
    with Connection() as con:
        for query in (
                r'σ Id > 1 Users',
                r'σ [ Id > 1 ] Users',
                r'σ [ Id > 1 ] ( Users )',
                r'σ[Id>1](Users)',
                r'Sigma Id > 1 Users',
                r'Sigma [ Id > 1 ] Users',
                r'Sigma [ Id > 1 ] ( Users )',
                r'Sigma[Id>1](Users)'
        ):
            root = RAParser.parse_query(query)

            assert isinstance(root, UnaryOperators.Selection)
            assert isinstance(root.target, RAOperand) and root.target.name == 'Users'
            assert isinstance(root.arg, LogicElement)

            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (2, 'Bob'),
                (3, 'Charlie')
            ]

        for query in (
                r'σ Id > 1 σ Id > 0 Users',
                r'σ [ Id > 1 ] (σ [Id > 1] (Users))',
                r'σ[Id>1]σ[Id>1]Users',
                r'Sigma Id > 1 Sigma Id > 0 Users',
                r'Sigma [ Id > 1 ] (Sigma [Id > 1] (Users))',
                r'Sigma[Id>1]Sigma[Id>1]Users'
        ):
            root = RAParser.parse_query(query)

            assert isinstance(root, UnaryOperators.Selection)
            assert isinstance(root.arg, LogicElement)
            assert isinstance(root.target, UnaryOperators.Selection)
            assert isinstance(root.target.arg, LogicElement)
            assert isinstance(root.target.target, RAOperand) and root.target.target.name == 'Users'

            cols, rows = con.execute_ra_return_cols(root)

            assert [c.lower() for c in cols] == [
                'id',
                'username'
            ]
            assert rows == [
                (2, 'Bob'),
                (3, 'Charlie')
            ]


def test_unary_inner_to_outer_evaluation_order():
    root = RAParser.parse_query(r'π [ Id ] π [ Id, Username ] (Users)')
    assert isinstance(root, UnaryOperators.Projection) and root.columns == ('Id',)
    assert isinstance(root.target, UnaryOperators.Projection) and root.target.columns == ('Id', 'Username')

    root = RAParser.parse_query(r'σ [ Id > 2 ] σ [ Id > 1 ] (Users)')
    assert isinstance(root, UnaryOperators.Selection)
    assert isinstance(root.condition, BinaryOperators.GreaterThan)
    assert root.condition.left == ('Id',) and root.condition.right == ('2',)
    assert isinstance(root.target, UnaryOperators.Selection)
    assert isinstance(root.target.condition, BinaryOperators.GreaterThan)
    assert root.target.condition.left == ('Id',) and root.target.condition.right == ('1',)

    root = RAParser.parse_query(r'β [ Id3 ← Id2 ] β [ Id2 ← Id ] (Users)')
    assert isinstance(root, UnaryOperators.Rename)
    assert isinstance(root.arrow, BinaryOperators.ArrowLeft)
    assert root.arrow.left == ('Id3',) and root.arrow.right == ('Id2',)
    assert isinstance(root.target, UnaryOperators.Rename)
    assert isinstance(root.target.arrow, BinaryOperators.ArrowLeft)
    assert root.target.arrow.left == ('Id2',) and root.target.arrow.right == ('Id',)


def test_binary_left_to_right_evaluation_order():
    # difference
    root = RAParser.parse_query(r'a \ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, BinaryOperators.Difference)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    # union
    root = RAParser.parse_query(r'a ∪ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, BinaryOperators.Union)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    # intersection
    root = RAParser.parse_query(r'a ∩ b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, BinaryOperators.Intersection)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    # natural join
    root = RAParser.parse_query(r'a ⋈ b ⋈ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, BinaryOperators.Join)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    # outer join
    root = RAParser.parse_query(r'a ⟕ b ⟕ c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟖ b ⟖ c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟗ b ⟗ c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    # mixed outer joins
    root = RAParser.parse_query(r'a ⟕ b ⟖ c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟕ b ⟗ c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟖ b ⟕ c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟖ b ⟗ c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟗ b ⟕ c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    root = RAParser.parse_query(r'a ⟗ b ⟖ c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'

    # cross join
    root = RAParser.parse_query(r'a x b x c')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.left, BinaryOperators.Cross)
    assert isinstance(root.left.left, RAOperand)
    assert root.left.left.name == 'a'
    assert isinstance(root.left.right, RAOperand)
    assert root.left.right.name == 'b'
    assert isinstance(root.right, RAOperand)
    assert root.right.name == 'c'


def test_unary_evaluation_order():
    root = RAParser.parse_query(r'π [ Id2 ] β [ Id2 ← Id ] (Users)')
    assert isinstance(root, UnaryOperators.Projection)
    assert isinstance(root.target, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] π [ Id ] (Users)')
    assert isinstance(root, UnaryOperators.Rename)
    assert isinstance(root.target, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] σ [ Id > 1 ] (Users)')
    assert isinstance(root, UnaryOperators.Projection)
    assert isinstance(root.target, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] π [ Id ] (Users)')
    assert isinstance(root, UnaryOperators.Selection)
    assert isinstance(root.target, UnaryOperators.Projection)

    root = RAParser.parse_query(r'σ [ Id2 > 1 ] β [ Id2 ← Id ] (Users)')
    assert isinstance(root, UnaryOperators.Selection)
    assert isinstance(root.target, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] σ [ Id > 1 ] (Users)')
    assert isinstance(root, UnaryOperators.Rename)
    assert isinstance(root.target, UnaryOperators.Selection)


def test_binary_evaluation_order():
    # difference <-> union
    root = RAParser.parse_query(r'a \ b ∪ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Union)

    root = RAParser.parse_query(r'a ∪ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Union)

    # difference <-> intersection
    root = RAParser.parse_query(r'a \ b ∩ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Intersection)

    root = RAParser.parse_query(r'a ∩ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Intersection)

    # difference <-> join
    root = RAParser.parse_query(r'a \ b ⋈ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Join)

    root = RAParser.parse_query(r'a ⋈ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Join)

    root = RAParser.parse_query(r'a \ b ⟕ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ⟕ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a \ b ⟖ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ⟖ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a \ b ⟗ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.FullOuterJoin)

    root = RAParser.parse_query(r'a ⟗ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.FullOuterJoin)

    # difference <-> cross
    root = RAParser.parse_query(r'a \ b x c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    # difference <-> division
    root = RAParser.parse_query(r'a \ b ÷ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b \ c')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    # union <-> intersection
    root = RAParser.parse_query(r'a ∪ b ∩ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Intersection)

    root = RAParser.parse_query(r'a ∩ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Intersection)

    # union <-> join
    root = RAParser.parse_query(r'a ∪ b ⋈ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Join)

    root = RAParser.parse_query(r'a ⋈ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Join)

    root = RAParser.parse_query(r'a ∪ b ⟕ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ⟕ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ∪ b ⟖ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ⟖ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ∪ b ⟗ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.FullOuterJoin)

    root = RAParser.parse_query(r'a ⟗ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.FullOuterJoin)

    # union <-> cross
    root = RAParser.parse_query(r'a ∪ b x c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    # union <-> division
    root = RAParser.parse_query(r'a ∪ b ÷ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b ∪ c')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    # intersection <-> join
    root = RAParser.parse_query(r'a ∩ b ⋈ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Join)

    root = RAParser.parse_query(r'a ⋈ b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Join)

    root = RAParser.parse_query(r'a ∩ b ⟕ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ⟕ b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ∩ b ⟖ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ⟖ b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ∩ b ⟗ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.FullOuterJoin)

    root = RAParser.parse_query(r'a ⟗ b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.FullOuterJoin)

    # intersection <-> cross
    root = RAParser.parse_query(r'a ∩ b x c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    # intersection <-> division
    root = RAParser.parse_query(r'a ∩ b ÷ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b ∩ c')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    # join <-> cross
    root = RAParser.parse_query(r'a ⋈ b x c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b ⋈ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a ⟕ b x c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b ⟕ c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a ⟖ b x c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b ⟖ c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a ⟗ b x c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Cross)

    root = RAParser.parse_query(r'a x b ⟗ c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Cross)

    # join <-> division
    root = RAParser.parse_query(r'a ⋈ b ÷ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b ⋈ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ⟕ b ÷ c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b ⟕ c')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ⟖ b ÷ c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b ⟖ c')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ⟗ b ÷ c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b ⟗ c')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)

    # natural join <-> outer join
    root = RAParser.parse_query(r'a ⋈ b ⟕ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ⟕ b ⋈ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.LeftOuterJoin)

    root = RAParser.parse_query(r'a ⋈ b ⟖ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ⟖ b ⋈ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.RightOuterJoin)

    root = RAParser.parse_query(r'a ⋈ b ⟗ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.FullOuterJoin)

    root = RAParser.parse_query(r'a ⟗ b ⋈ c')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.FullOuterJoin)

    # cross <-> division
    root = RAParser.parse_query(r'a x b ÷ c')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, BinaryOperators.Division)

    root = RAParser.parse_query(r'a ÷ b x c')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, BinaryOperators.Division)


def test_mixed_evaluation_order():
    # difference <-> projection
    root = RAParser.parse_query(r'a \ π [ Id ] b')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a \ b')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    # difference <-> rename
    root = RAParser.parse_query(r'a \ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a \ b')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    # difference <-> selection
    root = RAParser.parse_query(r'a \ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a \ b')
    assert isinstance(root, BinaryOperators.Difference)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    # union <-> projection
    root = RAParser.parse_query(r'a ∪ π [ Id ] b')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ∪ b')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    # union <-> rename
    root = RAParser.parse_query(r'a ∪ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ∪ b')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    # union <-> selection
    root = RAParser.parse_query(r'a ∪ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ∪ b')
    assert isinstance(root, BinaryOperators.Union)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    # intersection <-> projection
    root = RAParser.parse_query(r'a ∩ π [ Id ] b')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ∩ b')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    # intersection <-> rename
    root = RAParser.parse_query(r'a ∩ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ∩ b')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    # intersection <-> selection
    root = RAParser.parse_query(r'a ∩ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ∩ b')
    assert isinstance(root, BinaryOperators.Intersection)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    # join <-> projection
    root = RAParser.parse_query(r'a ⋈ π [ Id ] b')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ⋈ b')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    root = RAParser.parse_query(r'a ⟕ π [ Id ] b')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ⟕ b')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    root = RAParser.parse_query(r'a ⟖ π [ Id ] b')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ⟖ b')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    root = RAParser.parse_query(r'a ⟗ π [ Id ] b')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ⟗ b')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    # join <-> rename
    root = RAParser.parse_query(r'a ⋈ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ⋈ b')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    root = RAParser.parse_query(r'a ⟕ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ⟕ b')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    root = RAParser.parse_query(r'a ⟖ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ⟖ b')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    root = RAParser.parse_query(r'a ⟗ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ⟗ b')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    # join <-> selection
    root = RAParser.parse_query(r'a ⋈ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ⋈ b')
    assert isinstance(root, BinaryOperators.Join)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    root = RAParser.parse_query(r'a ⟕ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ⟕ b')
    assert isinstance(root, BinaryOperators.LeftOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    root = RAParser.parse_query(r'a ⟖ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ⟖ b')
    assert isinstance(root, BinaryOperators.RightOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    root = RAParser.parse_query(r'a ⟗ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ⟗ b')
    assert isinstance(root, BinaryOperators.FullOuterJoin)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    # cross <-> projection
    root = RAParser.parse_query(r'a x π [ Id ] b')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a x b')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    # cross <-> rename
    root = RAParser.parse_query(r'a x β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a x b')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    # cross <-> selection
    root = RAParser.parse_query(r'a x σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a x b')
    assert isinstance(root, BinaryOperators.Cross)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)

    # division <-> projection
    root = RAParser.parse_query(r'a ÷ π [ Id ] b')
    assert isinstance(root, BinaryOperators.Division)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Projection)

    root = RAParser.parse_query(r'π [ Id ] a ÷ b')
    assert isinstance(root, BinaryOperators.Division)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Projection)

    # division <-> rename
    root = RAParser.parse_query(r'a ÷ β [ Id2 ← Id ] b')
    assert isinstance(root, BinaryOperators.Division)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Rename)

    root = RAParser.parse_query(r'β [ Id2 ← Id ] a ÷ b')
    assert isinstance(root, BinaryOperators.Division)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Rename)

    # division <-> selection
    root = RAParser.parse_query(r'a ÷ σ [ Id > 1 ] b')
    assert isinstance(root, BinaryOperators.Division)
    assert isinstance(root.left, RAOperand) and isinstance(root.right, UnaryOperators.Selection)

    root = RAParser.parse_query(r'σ [ Id > 1 ] a ÷ b')
    assert isinstance(root, BinaryOperators.Division)
    assert isinstance(root.right, RAOperand) and isinstance(root.left, UnaryOperators.Selection)


def test_special_queries():
    with Connection() as con:
        # Consecutive operators triggered a recursion error in a previous
        # version, leading to an infinite loop / stack overflow.
        with pytest.raises(RAParserError, match='right operand missing after x'):
            RAParser.parse_query(r'''
                Users x x BannedUsers
            ''')

        # Enclosing parentheses are removed. In the following case
        # the parentheses may only be removed from each subquery
        # independently *after* the cross join is applied. Otherwise,
        # the result is a parsing error.
        root = RAParser.parse_query(r'''
            (
              Sigma [ Id > 1 ] Pi [ Username, Id ] (Users)
            ) x (
              Beta [ Username2 <- BannedUsername ] Beta [ Id2 <- Id ] (BannedUsers)
            )
        ''')

        assert isinstance(root, BinaryOperators.Cross)
        assert isinstance(root.left, UnaryOperators.Selection)
        assert isinstance(root.left.target, UnaryOperators.Projection)
        assert isinstance(root.left.target.target, RAOperand) and root.left.target.target.name == 'Users'
        assert isinstance(root.right, UnaryOperators.Rename)
        assert isinstance(root.right.target, UnaryOperators.Rename)
        assert isinstance(root.right.target.target, RAOperand) and root.right.target.target.name == 'BannedUsers'

        assert con.execute_ra(root) == [
            ('Bob', 2, 2, 'Bob'),
            ('Bob', 2, 4, 'David'),
            ('Charlie', 3, 2, 'Bob'),
            ('Charlie', 3, 4, 'David')
        ]
