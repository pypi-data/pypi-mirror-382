import pytest

from src.py_cdll.exceptions import IndexNotFoundError, IndexOutOfRangeError
from src.py_cdll.node import Node, nodes_from_values, node_with_index, is_consistent, is_value_at_index


def test_node_with_index_one_node_index_zero_success():
    # Setup
    values0: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    node1: Node = node_with_index(node=node0, index=0)

    # Validation
    assert node0 is node1
    assert is_consistent(node=node0)
    assert is_value_at_index(node=node0, reference=values0)


def test_node_with_index_two_nodes_index_one_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    node1: Node = node_with_index(node=node0, index=1)

    # Validation
    assert is_consistent(node=node0)
    assert is_value_at_index(node=node0, reference=values0)
    assert is_value_at_index(node=node1, reference=values0)


def test_node_with_index_seven_nodes_index_five_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    node1: Node = node_with_index(node=node0, index=5)

    # Validation
    assert is_consistent(node=node0)
    assert is_value_at_index(node=node0, reference=values0)
    assert is_value_at_index(node=node1, reference=values0)


def test_node_with_index_seven_nodes_index_seven_out_of_range_failure():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six"]
    node0: Node = nodes_from_values(values=values0)

    # Validation
    with pytest.raises(IndexOutOfRangeError):
        _ = node_with_index(node=node0, index=7)


def test_node_with_index_four_nodes_index_minus_two_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three"]
    node0: Node = nodes_from_values(values=values0)

    # Validation
    with pytest.raises(IndexNotFoundError):
        _ = node_with_index(node=node0, index=-2)
