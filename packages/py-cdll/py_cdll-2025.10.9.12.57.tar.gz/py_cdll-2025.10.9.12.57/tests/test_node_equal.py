from src.py_cdll.node import Node, equal, nodes_from_values


def test_equal_one_value_same_success():
    # Setup
    values0: list[str] = ["value0"]
    first0: Node = nodes_from_values(values=values0)
    second0: Node = nodes_from_values(values=values0)
    boolean0: bool = True

    # Execution
    boolean1: bool = equal(first=first0, second=second0)

    # Validation
    assert boolean0 is boolean1


def test_equal_one_value_different_values_success():
    # Setup
    values0: list[str] = ["value0"]
    values1: list[str] = ["value1"]
    first0: Node = nodes_from_values(values=values0)
    second0: Node = nodes_from_values(values=values1)
    boolean0: bool = False

    # Execution
    boolean1: bool = equal(first=first0, second=second0)

    # Validation
    assert boolean0 is boolean1


def test_equal_two_values_different_lengths_success():
    # Setup
    values0: list[str] = ["value0"]
    values1: list[str] = ["value0", "value1"]
    first0: Node = nodes_from_values(values=values0)
    second0: Node = nodes_from_values(values=values1)
    boolean0: bool = False

    # Execution
    boolean1: bool = equal(first=first0, second=second0)

    # Validation
    assert boolean0 is boolean1


def test_equal_two_values_same_success():
    # Setup
    values0: list[str] = ["value0", "value1"]
    first0: Node = nodes_from_values(values=values0)
    second0: Node = nodes_from_values(values=values0)
    boolean0: bool = True

    # Execution
    boolean1: bool = equal(first=first0, second=second0)

    # Validation
    assert boolean0 is boolean1


def test_equal_two_values_different_values_success():
    # Setup
    values0: list[str] = ["value0", "value1"]
    values1: list[str] = ["value0", "value2"]
    first0: Node = nodes_from_values(values=values0)
    second0: Node = nodes_from_values(values=values1)
    boolean0: bool = False

    # Execution
    boolean1: bool = equal(first=first0, second=second0)

    # Validation
    assert boolean0 is boolean1


def test_equal_two_values_same_index_head_different_success():
    # Setup
    values0: list[str] = ["value0", "value1"]
    values1: list[str] = ["value1", "value0"]
    first0: Node = nodes_from_values(values=values0)
    second0: Node = nodes_from_values(values=values1)
    second1: Node = second0.next
    boolean0: bool = False

    # Execution
    boolean1: bool = equal(first=first0, second=second1)

    # Validation
    assert boolean0 is boolean1
