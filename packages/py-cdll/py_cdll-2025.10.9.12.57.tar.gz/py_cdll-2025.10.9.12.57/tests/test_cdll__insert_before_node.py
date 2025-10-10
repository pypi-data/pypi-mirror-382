import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import Node, is_consistent, is_value_at_index


def test__insert_before_node_one_in_list_insert_not_node_failure():
    # Setup
    node0: str = "string"
    cdll0: CDLL = CDLL(values=[None])

    # Validation
    with pytest.raises(AttributeError):
        # noinspection PyTypeChecker
        cdll0._insert_before_node(anchor=cdll0._head, insert=node0)


def test__insert_before_node_one_in_list_insert_one_and_reassign_head_success():
    # Setup
    data0: int = 0
    data1: int = 1
    values0: list[int] = [data0]
    values1: list[int] = [data1, data0]
    node0: Node = Node(value=data1)
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._insert_before_node(anchor=cdll0._head, insert=node0)

    # Validation
    assert cdll0._last.next is node0
    assert cdll0._last.previous is node0
    assert node0.next is cdll0._last
    assert node0.previous is cdll0._last
    assert len(cdll0) == 2
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test__insert_before_node_two_in_list_insert_one_in_middle_success():
    # Setup
    data0: int = 0
    data1: int = 1
    data2: int = 2
    values0: list[int] = [data0, data1]
    values1: list[int] = [data0, data2, data1]
    node0: Node = Node(value=data2)
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._insert_before_node(anchor=cdll0._last, insert=node0)

    # Validation
    assert cdll0._head.next is node0
    assert cdll0._last.previous is node0
    assert node0.next is cdll0._last
    assert node0.previous is cdll0._head
    assert len(cdll0) == 3
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test__insert_before_node_four_in_list_insert_one_in_middle_success():
    # Setup
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    values0: list[int] = [data0, data1, data3, data4]
    values1: list[int] = [data0, data1, data2, data3, data4]
    node0: Node = Node(value=data2)
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._insert_before_node(anchor=cdll0._last.previous, insert=node0)

    # Validation
    assert cdll0._head.next.next is node0
    assert cdll0._last.previous.previous is node0
    assert node0.next.next is cdll0._last
    assert node0.previous.previous is cdll0._head
    assert len(cdll0) == 5
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)
