from src.py_cdll import CDLL
from src.py_cdll.node import Node, is_consistent, is_value_at_index


def test__node_remove_from_single_success():
    # Setup
    values0: list[int] = [0]
    cdll0: CDLL = CDLL(values=values0)
    node0: Node = cdll0._head

    # Execution
    cdll0._node_remove(target=node0)

    # Validation
    assert node0 not in cdll0._nodes()
    assert len(cdll0) == 0
    assert cdll0.is_empty() is True


def test__node_remove_head_from_triple_success():
    # Bug: _node_remove had no check for whether head was being removed, which would invalidate pointer in CDLL
    # and cause infinite loops when trying to find head after that.

    # Setup
    values0: list[int] = [0, 1, 2]
    values1: list[int] = [1, 2]
    cdll0: CDLL = CDLL(values=values0)
    node0: Node = cdll0._head

    # Execution
    cdll0._node_remove(target=node0)

    # Validation
    assert node0 not in cdll0._nodes()
    assert len(cdll0) == 2
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test__node_remove_from_multiple_success():
    # Setup
    values0: list[int] = [0, 1, 2, 3, 4]
    values1: list[int] = [0, 1, 2, 4]
    cdll0: CDLL = CDLL(values=values0)
    node0: Node = cdll0._head.previous.previous

    # Execution
    cdll0._node_remove(target=node0)

    # Validation
    assert node0 not in cdll0._nodes()
    assert len(cdll0) == 4
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)
