import pytest

from src.py_cdll import NotANodeError
from src.py_cdll.node import Node, length, insert_between, is_consistent


def test_length_not_node_failure():
    # Setup
    node0: float = 3.14

    # Validation
    with pytest.raises(NotANodeError):
        # noinspection PyTypeChecker
        length(node=node0)


def test_length_one_node_success():
    # Setup
    node0: Node = Node(value=None)
    length0: int = 1

    # Execution
    length1: int = length(node=node0)

    # Validation
    assert length0 == length1
    assert is_consistent(node=node0) is True


def test_length_two_nodes_success():
    # Setup
    node0: Node = Node(value=None)
    node1: Node = Node(value=None)
    insert_between(before=node0, after=node0, insert=node1)
    length0: int = 2

    # Execution
    length1: int = length(node=node0)

    # Validation
    assert length0 == length1
    assert is_consistent(node=node0) is True


def test_length_three_nodes_success():
    # Setup
    node0: Node = Node(value=None)
    node1: Node = Node(value=None)
    node2: Node = Node(value=None)
    insert_between(before=node0, after=node0, insert=node1)
    insert_between(before=node1, after=node0, insert=node2)
    length0: int = 3

    # Execution
    length1: int = length(node=node0)

    # Validation
    assert length0 == length1
    assert is_consistent(node=node0) is True


def test_length_four_nodes_success():
    # Setup
    node0: Node = Node(value=None)
    node1: Node = Node(value=None)
    node2: Node = Node(value=None)
    node3: Node = Node(value=None)
    insert_between(before=node1, after=node1, insert=node2)
    insert_between(before=node0, after=node0, insert=node1)
    insert_between(before=node2, after=node0, insert=node3)
    length0: int = 4

    # Execution
    length1: int = length(node=node0)

    # Validation
    assert length0 == length1
    assert is_consistent(node=node0) is True
