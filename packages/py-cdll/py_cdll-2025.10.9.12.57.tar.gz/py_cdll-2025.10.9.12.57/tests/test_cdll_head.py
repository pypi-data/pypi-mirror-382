import pytest

from src.py_cdll import CDLL, EmptyCDLLError


def test_head_of_empty_list_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        _ = cdll0.head


def test_head_after_init_success():
    # Setup
    data: str = "data"
    cdll0 = CDLL(values=[data])

    # Validation
    assert cdll0.head == data
    assert cdll0.last == data
