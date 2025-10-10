import pytest

from src.py_cdll import CDLL, EmptyCDLLError, ValueNotFoundError, MultipleValuesFoundError


def test_index_unique_with_empty_list_failure():
    # Setup
    data0 = "data0"
    list0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        list0.index_unique(data0)


def test_index_unique_with_single_option_single_hit_success():
    # Setup
    data0 = "data0"
    list0: CDLL = CDLL()
    list0.append(data0)

    # Validation
    assert list0.index_unique(data0) == 0


def test_index_unique_with_multiple_options_single_hit_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)

    # Validation
    assert list0.index_unique(data1) == 1


def test_index_unique_with_zero_hit_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)

    # Validation
    with pytest.raises(ValueNotFoundError):
        list0.index_unique(data)


def test_index_unique_with_multiple_hits_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    list0: CDLL = CDLL()
    list0.append(data)
    list0.append(data0)
    list0.append(data)
    list0.append(data1)
    list0.append(data)
    list0.append(data2)
    list0.append(data)

    # Validation
    with pytest.raises(MultipleValuesFoundError):
        list0.index_unique(data)
