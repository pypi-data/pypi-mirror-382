from duckdb_kernel.util.ResultSetComparator import ResultSetComparator


def test_equals():
    rsc = ResultSetComparator([
        (1, "Alice"),
        (3, "Charlie")
    ], [
        (1, "Alice"),
        (3, "Charlie")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == []
    assert rsc.ordered_left_only == []
    assert rsc.ordered_right_only == []


def test_equals_only_unordered():
    rsc = ResultSetComparator([
        (1, "Alice"),
        (3, "Charlie")
    ], [
        (3, "Charlie"),
        (1, "Alice")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == []
    assert rsc.ordered_left_only == [(3, "Charlie")]
    assert rsc.ordered_right_only == [(1, "Alice")]


def test_missing():
    # first missing
    rsc = ResultSetComparator([
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == [(1, "Alice")]
    assert rsc.right_only == []
    assert rsc.ordered_left_only == [(1, "Alice")]
    assert rsc.ordered_right_only == []

    # middle missing
    rsc = ResultSetComparator([
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (1, "Alice"),
        (3, "Charlie")
    ])

    assert rsc.left_only == [(2, "Bob")]
    assert rsc.right_only == []
    assert rsc.ordered_left_only == [(2, "Bob")]
    assert rsc.ordered_right_only == []

    # last missing
    rsc = ResultSetComparator([
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (1, "Alice"),
        (2, "Bob")
    ])

    assert rsc.left_only == [(3, "Charlie")]
    assert rsc.right_only == []
    assert rsc.ordered_left_only == [(3, "Charlie")]
    assert rsc.ordered_right_only == []


def test_unnecessary():
    # first unnecessary
    rsc = ResultSetComparator([
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == [(1, "Alice")]
    assert rsc.ordered_left_only == []
    assert rsc.ordered_right_only == [(1, "Alice")]

    # middle unnecessary
    rsc = ResultSetComparator([
        (1, "Alice"),
        (3, "Charlie")
    ], [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == [(2, "Bob")]
    assert rsc.ordered_left_only == []
    assert rsc.ordered_right_only == [(2, "Bob")]

    # last unnecessary
    rsc = ResultSetComparator([
        (1, "Alice"),
        (2, "Bob")
    ], [
        (1, "Alice"),
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == [(3, "Charlie")]
    assert rsc.ordered_left_only == []
    assert rsc.ordered_right_only == [(3, "Charlie")]


def test_repeating():
    # equal
    rsc = ResultSetComparator([
        (2, "Bob"),
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (2, "Bob"),
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == []
    assert rsc.ordered_left_only == []
    assert rsc.ordered_right_only == []

    # missing
    rsc = ResultSetComparator([
        (2, "Bob"),
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == [(2, "Bob")]
    assert rsc.right_only == []
    assert rsc.ordered_left_only == [(2, "Bob")]
    assert rsc.ordered_right_only == []

    # unnecessary
    rsc = ResultSetComparator([
        (2, "Bob"),
        (3, "Charlie")
    ], [
        (2, "Bob"),
        (2, "Bob"),
        (3, "Charlie")
    ])

    assert rsc.left_only == []
    assert rsc.right_only == [(2, "Bob")]
    assert rsc.ordered_left_only == []
    assert rsc.ordered_right_only == [(2, "Bob")]
