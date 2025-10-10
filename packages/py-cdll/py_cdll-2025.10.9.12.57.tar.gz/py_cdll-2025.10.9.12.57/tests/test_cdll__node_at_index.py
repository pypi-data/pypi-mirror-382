import pytest

from src.py_cdll import CDLL, EmptyCDLLError
from src.py_cdll.node import Node


def test__node_at_index_first_index_in_zero_items_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        cdll0._node_at_index(index=1)


def test__node_at_index_eighth_index_in_four_items_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data0, data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(IndexError):
        cdll0._node_at_index(index=8)


def test__node_at_index_zeroth_index_in_one_item_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_at_index(index=0)

    # Validation
    assert node0 is cdll0._head


def test__node_at_index_first_index_in_two_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    datas0: list[str] = [data0, data1]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_at_index(index=1)

    # Validation
    assert node0 is cdll0._last


def test__node_at_index_second_index_in_four_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data0, data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_at_index(index=2)

    # Validation
    assert node0 is cdll0._head.next.next
    assert node0 is cdll0._last.previous
