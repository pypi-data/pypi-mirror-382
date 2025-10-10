import pytest

from src.py_cdll import CDLL, EmptyCDLLError


def test_last_empty_list_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        _ = cdll0.last


def test_last_success():
    # Setup
    data0: str = "head"
    data1: str = "end"
    datas0: list[str] = [data0, data1]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    assert cdll0.head == data0
    assert cdll0.last == data1
