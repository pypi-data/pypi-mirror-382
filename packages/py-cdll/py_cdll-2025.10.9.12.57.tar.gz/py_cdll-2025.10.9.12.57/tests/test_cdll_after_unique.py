import pytest

from src.py_cdll import CDLL, NoAdjacentValueError, EmptyCDLLError


def test_after_unique_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)

    # Validation
    assert list0.after_unique(data2) is data0


def test_after_unique_single_entry_list_failure():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()
    list0.append(data0)

    # Validation
    with pytest.raises(NoAdjacentValueError):
        list0.after_unique(data0)


def test_after_unique_empty_list_failure():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        list0.after_unique(data0)
