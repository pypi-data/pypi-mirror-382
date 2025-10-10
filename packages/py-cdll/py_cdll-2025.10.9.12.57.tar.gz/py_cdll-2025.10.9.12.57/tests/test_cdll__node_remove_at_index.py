import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import Node


def test__node_remove_at_index_positive_index_in_range_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)
    index0: int = 2

    # Execution
    node0: Node = cdll0._node_remove_at_index(index=index0)

    # Validation
    assert node0.value == data2
    assert data2 not in cdll0


def test__node_remove_at_index_negative_index_in_range_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)
    index0: int = -2

    # Execution
    node0: Node = cdll0._node_remove_at_index(index=index0)

    # Validation
    assert node0.value == data3
    assert data3 not in cdll0


def test__node_remove_at_index_positive_index_out_of_range_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)
    index0: int = 11

    # Validation
    with pytest.raises(IndexError):
        cdll0._node_remove_at_index(index=index0)


def test__node_remove_at_index_negative_index_out_of_range_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)
    index0: int = -8

    # Validation
    with pytest.raises(IndexError):
        cdll0._node_remove_at_index(index=index0)
