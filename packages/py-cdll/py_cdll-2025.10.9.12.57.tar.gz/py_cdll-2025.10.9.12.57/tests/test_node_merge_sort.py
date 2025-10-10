import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import merge_sort, nodes_from_values, Node, equal, is_consistent


def test_merge_sort_integers_success():
    # Setup
    values0 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    values1 = [2, 0, 9, 7, 4, 5, 6, 3, 8, 1]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values1)

    # Execution
    node2: Node = merge_sort(head=node1)

    # Validation
    assert equal(first=node0, second=node2)
    assert is_consistent(node=node2) is True


def test_merge_sort_strings_success():
    # Setup
    values0 = ["a", "d", "f", "j", "m", "p", "q", "t", "v", "y"]
    values1 = ['t', 'v', 'y', 'j', 'm', 'a', 'p', 'q', 'd', 'f']
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values1)

    # Execution
    node2: Node = merge_sort(head=node1)

    # Validation
    assert equal(first=node0, second=node2)
    assert is_consistent(node=node2) is True


def test_merge_sort_functions_failure():
    # Setup
    l0 = [min, max, all]
    c0 = CDLL(l0)

    # Validation
    with pytest.raises(TypeError):
        merge_sort(head=c0._head)
