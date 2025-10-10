import pytest

from src.py_cdll import CDLL


def test__normalize_index_value_zero_success():
    # Setup
    values0: range = range(5)
    cdll0: CDLL = CDLL()
    [cdll0.append(value) for value in values0]
    index0: int = 0

    # Execution
    index1: int = cdll0._normalize_index(index=index0)

    # Validation
    assert index0 == index1


def test__normalize_index_value_positive_success():
    # Setup
    values0: range = range(8)
    cdll0: CDLL = CDLL()
    [cdll0.append(value) for value in values0]
    index0: int = 4

    # Execution
    index1: int = cdll0._normalize_index(index=index0)

    # Validation
    assert index0 == index1


def test__normalize_index_value_negative_success():
    # Setup
    values0: range = range(11)
    cdll0: CDLL = CDLL()
    [cdll0.append(value) for value in values0]
    index0: int = -6
    index1: int = 5

    # Execution
    index2: int = cdll0._normalize_index(index=index0)

    # Validation
    assert index1 == index2


def test__normalize_index_value_positive_out_of_range_failure():
    # Setup
    values0: range = range(20)
    cdll0: CDLL = CDLL()
    [cdll0.append(value) for value in values0]
    index0: int = 25

    # Validation
    with pytest.raises(IndexError):
        cdll0._normalize_index(index=index0)


def test__normalize_index_value_negative_out_of_range_failure():
    # Setup
    values0: range = range(37)
    cdll0: CDLL = CDLL()
    [cdll0.append(value) for value in values0]
    index0: int = -45

    # Validation
    with pytest.raises(IndexError):
        cdll0._normalize_index(index=index0)
