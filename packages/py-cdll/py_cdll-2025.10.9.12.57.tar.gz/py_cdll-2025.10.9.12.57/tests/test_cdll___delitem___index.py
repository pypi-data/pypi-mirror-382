import pytest

from src.py_cdll import CDLL


def test___delitem___index_positive_in_range_success():
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
    del cdll0[index0]

    # Validation
    assert data2 not in cdll0
    assert cdll0._head.value is data0
    assert cdll0._head.next.value is data1
    assert cdll0._head.next.next.value is data3
    assert cdll0._head.next.next.next.value is data4
    assert cdll0._head.next.next.next is cdll0._last
    assert cdll0._last.previous.previous.previous is cdll0._head


def test___delitem___index_negative_in_range_success():
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
    del cdll0[index0]

    # Validation
    assert data3 not in cdll0
    assert cdll0._head.value is data0
    assert cdll0._head.next.value is data1
    assert cdll0._head.next.next.value is data2
    assert cdll0._head.next.next.next.value is data4
    assert cdll0._head.next.next.next is cdll0._last
    assert cdll0._last.previous.previous.previous is cdll0._head


def test___delitem___index_positive_out_of_range_failure():
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
        del cdll0[index0]


def test___delitem___index_negative_out_of_range_failure():
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
        del cdll0[index0]
