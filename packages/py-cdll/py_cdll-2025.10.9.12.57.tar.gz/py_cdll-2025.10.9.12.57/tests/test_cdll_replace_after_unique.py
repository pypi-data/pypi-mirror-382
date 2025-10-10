import pytest

from src.py_cdll import CDLL, NoAdjacentValueError
from src.py_cdll.node import is_consistent, is_value_at_index


def test_replace_after_unique_overwrite_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data0, data, data2]
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0.replace_after_unique(value=data0, replacement=data)

    # Validation
    assert cdll0.after_unique(value=data0) is data
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test_replace_after_unique_single_entry_list_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    values0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(NoAdjacentValueError):
        cdll0.replace_after_unique(value=data0, replacement=data1)
