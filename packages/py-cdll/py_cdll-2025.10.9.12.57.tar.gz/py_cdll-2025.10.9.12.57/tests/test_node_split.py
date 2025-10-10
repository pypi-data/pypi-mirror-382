import pytest

from src.py_cdll import NodesNotInSameListError
from src.py_cdll.node import Node, nodes_from_values, split, equal, is_consistent, is_value_at_index


def test_split_one_node_one_head_one_list_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values0)

    # Execution
    split(first_head=node0, second_head=node0)

    # Validation
    assert equal(first=node0, second=node1)
    assert is_consistent(node=node0) is True
    assert is_value_at_index(node=node0, reference=values0) is True
    assert is_value_at_index(node=node1, reference=values0) is True


def test_split_two_nodes_one_head_one_list_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values0)

    # Execution
    split(first_head=node0, second_head=node0)

    # Validation
    assert equal(first=node0, second=node1)
    assert is_consistent(node=node0) is True
    assert is_value_at_index(node=node0, reference=values0) is True
    assert is_value_at_index(node=node1, reference=values0) is True


def test_split_two_nodes_two_heads_one_list_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    values1: list[str] = ["zero"]
    values2: list[str] = ["one"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next
    node2: Node = nodes_from_values(values=values1)
    node3: Node = nodes_from_values(values=values2)

    # Execution
    split(first_head=node0, second_head=node1)

    # Validation
    assert equal(first=node0, second=node2)
    assert equal(first=node1, second=node3)
    assert is_consistent(node=node0) is True
    assert is_consistent(node=node1) is True
    assert is_value_at_index(node=node0, reference=values1) is True
    assert is_value_at_index(node=node1, reference=values2) is True


def test_split_three_nodes_two_heads_one_list_success():
    # Setup
    values0: list[str] = ["zero", "one", "two"]
    values1: list[str] = ["zero", "one"]
    values2: list[str] = ["two"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next.next
    node2: Node = nodes_from_values(values=values1)
    node3: Node = nodes_from_values(values=values2)

    # Execution
    split(first_head=node0, second_head=node1)

    # Validation
    assert equal(first=node0, second=node2)
    assert equal(first=node1, second=node3)
    assert is_consistent(node=node0) is True
    assert is_consistent(node=node1) is True
    assert is_value_at_index(node=node0, reference=values1) is True
    assert is_value_at_index(node=node1, reference=values2) is True


def test_split_four_nodes_two_heads_one_list_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three"]
    values1: list[str] = ["zero", "one"]
    values2: list[str] = ["two", "three"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next.next
    node2: Node = nodes_from_values(values=values1)
    node3: Node = nodes_from_values(values=values2)

    # Execution
    split(first_head=node0, second_head=node1)

    # Validation
    assert equal(first=node0, second=node2)
    assert equal(first=node1, second=node3)
    assert is_consistent(node=node0) is True
    assert is_consistent(node=node1) is True
    assert is_value_at_index(node=node0, reference=values1) is True
    assert is_value_at_index(node=node1, reference=values2) is True


def test_split_two_nodes_two_heads_two_lists_failure():
    # Setup
    values0: list[str] = ["zero", "one"]
    values1: list[str] = ["zero", "one"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values1)

    # Validation
    with pytest.raises(NodesNotInSameListError):
        split(first_head=node0, second_head=node1)
