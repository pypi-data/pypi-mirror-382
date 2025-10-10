import pytest

from src.py_cdll import CDLL
from src.py_cdll.exceptions import CDLLAlreadyPopulatedError, UnableToPopulateWithNoValuesError
from src.py_cdll.node import is_consistent, is_value_at_index


def test__populate_non_empty_cdll_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    values0: list[str] = [data0]
    values1: list[str] = [data1]
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(CDLLAlreadyPopulatedError):
        cdll0._populate(values=values1)


def test__populate_empty_cdll_with_no_values_failure():
    # Setup
    values0: list[str] = []
    values1: list[str] = []
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(UnableToPopulateWithNoValuesError):
        cdll0._populate(values=values1)


def test__populate_empty_cdll_success():
    # Setup
    data0: str = "data0"
    values0: list[str] = [data0]
    cdll0: CDLL = CDLL()

    # Execution
    cdll0._populate(values=values0)

    # Validation
    assert cdll0.head == data0
    assert cdll0._head == cdll0._head.next
    assert cdll0._head == cdll0._head.previous
    assert len(cdll0) == 1
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values0)
