import pytest

from src.py_cdll import CDLL, NoAdjacentValueError, EmptyCDLLError


def test_before_unique_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)

    # Validation
    assert list0.before_unique(data2) is data1


def test_before_unique_single_entry_list_failure():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()
    list0.append(data0)

    # Validation
    with pytest.raises(NoAdjacentValueError):
        list0.before_unique(data0)


def test_before_unique_empty_list_failure():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        list0.before_unique(data0)
