import pytest

from src.py_cdll import CDLL, EmptyCDLLError


def test__head_empty_success():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        _ = cdll0._last


def test__head_three_items_success():
    # Setup
    data0: int = 0
    data1: int = 1
    data2: int = 2
    datas0: list[int] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    assert cdll0._last.previous is cdll0._last.next.next
    assert cdll0._last.previous.previous is cdll0._last.next
    assert cdll0._last.previous.previous.previous is cdll0._last
    assert cdll0._last.next.next.next is cdll0._last
