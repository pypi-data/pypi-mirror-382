import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import Node, is_consistent, is_value_at_index, length


def test___setitem___index_looping_over_and_replacing_all_success():
    # Setup
    data0: int = 37
    data1: int = 73
    values0: list[int] = [data0, data1]
    values1: list[int] = [0, 1]
    cdll0: CDLL = CDLL(values=values0)
    node0: Node = cdll0._head
    node1: Node = cdll0._head.next

    # Verification
    assert node0.value == data0
    assert node1.value == data1
    assert is_consistent(cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values0)

    # Execution
    for index, _ in enumerate(cdll0):
        cdll0[index] = index

    # Validation
    assert cdll0._head.value == 0
    assert cdll0._last.value == 1
    assert cdll0._head.next is cdll0._last
    assert cdll0._head.previous is cdll0._last
    assert cdll0._head is cdll0._head.head
    assert is_consistent(cdll0._head)
    assert is_consistent(node0)
    assert is_consistent(node1)
    assert is_value_at_index(node=cdll0._head, reference=values1)
    assert is_value_at_index(node=node0, reference=values0[0:1])
    assert is_value_at_index(node=node1, reference=values0[1:])


def test___setitem___four_items_change_head_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    values0: list[str] = [data0, data1, data2, data3]
    values1: list[str] = [data, data1, data2, data3]
    values2: list[str] = [data0]
    cdll0: CDLL = CDLL(values=values0)
    node0: Node = cdll0._head

    # Execution
    cdll0[0] = data

    # Validation
    assert cdll0._head.value is data
    assert cdll0._head is cdll0._head.head
    assert length(node=node0) == 1
    assert is_consistent(node0)
    assert is_consistent(cdll0._head)
    assert is_value_at_index(node=node0, reference=values2)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test___setitem___index_in_range_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])
    node0: Node = cdll0._head

    # Execution
    cdll0[0] = data1

    # Validation
    assert cdll0._head.value is data1
    assert cdll0._head is cdll0._head.head
    assert cdll0._head.next is cdll0._head
    assert cdll0._head.previous is cdll0._head
    assert is_consistent(cdll0._head)
    assert is_consistent(node0)


def test___setitem___index_out_of_range_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])

    # Validation
    with pytest.raises(IndexError):
        cdll0[1] = data1


def test___setitem___index_empty_list_out_of_range_failure():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0[0] = data0


def test___setitem___index_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1]
    cdll0: CDLL = CDLL(values=datas0)
    node0: Node = cdll0._head
    node1: Node = cdll0._head.next

    # Verification
    assert cdll0._head.value is data0
    assert cdll0._last.value is data1
    assert cdll0._head.next is cdll0._last
    assert cdll0._head.previous is cdll0._last
    assert cdll0._last.next is cdll0._head
    assert cdll0._last.previous is cdll0._head

    # Execution
    cdll0[-1] = data2

    # Validation
    assert cdll0._head.value is data0
    assert cdll0._last.value is data2
    assert cdll0._head is cdll0._head.head
    assert cdll0._head.next is cdll0._last
    assert cdll0._head.previous is cdll0._last
    assert cdll0._last.next is cdll0._head
    assert cdll0._last.previous is cdll0._head
    assert is_consistent(cdll0._head)
    assert is_consistent(node0)
    assert is_consistent(node1)
