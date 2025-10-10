import pytest

from src.py_cdll import CDLL, EmptyCDLLError


def test___getitem___index_in_range_success():
    # Setup
    head: str = "head"
    cdll0: CDLL = CDLL(values=[head])

    # Execution
    first_item: str = cdll0[0]

    # Validation
    assert first_item is head


def test___getitem___index_out_of_range_failure():
    # Setup
    head: str = "head"
    cdll0: CDLL = CDLL(values=[head])

    # Validation
    with pytest.raises(IndexError):
        _ = cdll0[1]


def test___getitem___index_of_empty_list_out_of_range_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        _ = cdll0[0]


def test___getitem___negative_index_success():
    # Setup
    data0: int = 100
    data1: int = 200
    data2: int = 300
    datas0: list[int] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    last_item: int = cdll0[-1]

    # Validation
    assert last_item is data2
