import pytest

from src.py_cdll import CDLL, EmptyCDLLError
from src.py_cdll.exceptions import NoBeforeAndAfterUniqueError, NoAdjacentValueError


def test_before_and_after_unique_three_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)

    # Execution
    previous0, next0 = list0.before_and_after_unique(value=data1)

    # Validation
    assert previous0 == data0 and next0 == data2


def test_before_and_after_unique_six_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)
    list0.append(data3)
    list0.append(data4)
    list0.append(data5)

    # Execution
    previous0, next0 = list0.before_and_after_unique(value=data4)

    # Validation
    assert previous0 == data3 and next0 == data5


def test_before_and_after_unique_two_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)

    # Validation
    with pytest.raises(NoAdjacentValueError):
        list0.before_and_after_unique(value=data1)


def test_before_and_after_unique_one_item_success():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()
    list0.append(data0)

    # Validation
    with pytest.raises(NoAdjacentValueError):
        list0.before_and_after_unique(value=data0)


def test_before_and_after_unique_zero_items_failure():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        list0.before_and_after_unique(value=data0)


def test_before_and_after_unique_four_items_not_found_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)
    list0.append(data3)

    # Validation
    with pytest.raises(NoBeforeAndAfterUniqueError):
        list0.before_and_after_unique(value=data)


def test_before_and_after_unique_seven_items_multiple_found_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    list0: CDLL = CDLL()
    list0.append(data0)
    list0.append(data1)
    list0.append(data2)
    list0.append(data3)
    list0.append(data4)
    list0.append(data3)
    list0.append(data3)

    # Validation
    with pytest.raises(NoBeforeAndAfterUniqueError):
        list0.before_and_after_unique(value=data3)
