import pytest

from src.py_cdll import CDLL, EmptyCDLLError, UnevenListLengthError, ValueNotFoundError, MultipleValuesFoundError


def test_opposite_two_items_from_zero_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)

    # Execution
    data2: str = list0.opposite_unique(value=data0)

    # Validation
    assert data2 == data1


def test_opposite_four_items_from_one_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)
    list0.append(value=data2)
    list0.append(value=data3)

    # Execution
    data4: str = list0.opposite_unique(value=data1)

    # Validation
    assert data4 == data3


def test_opposite_sixteen_items_from_thirteen_across_zero_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    data7: str = "data7"
    data8: str = "data8"
    data9: str = "data9"
    data10: str = "data10"
    data11: str = "data11"
    data12: str = "data12"
    data13: str = "data13"
    data14: str = "data14"
    data15: str = "data15"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)
    list0.append(value=data2)
    list0.append(value=data3)
    list0.append(value=data4)
    list0.append(value=data5)
    list0.append(value=data6)
    list0.append(value=data7)
    list0.append(value=data8)
    list0.append(value=data9)
    list0.append(value=data10)
    list0.append(value=data11)
    list0.append(value=data12)
    list0.append(value=data13)
    list0.append(value=data14)
    list0.append(value=data15)

    # Execution
    data16: str = list0.opposite_unique(value=data13)

    # Validation
    assert data16 == data5


def test_opposite_empty_list_data_not_found_error_failure():
    # Setup
    data0: str = "data0"

    list0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        list0.opposite_unique(value=data0)


def test_opposite_one_item_failure():
    # Setup
    data0: str = "data0"

    list0: CDLL = CDLL()
    list0.append(value=data0)

    # Validation
    with pytest.raises(UnevenListLengthError):
        list0.opposite_unique(value=data0)


def test_opposite_five_items_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data0"
    data2: str = "data0"
    data3: str = "data0"
    data4: str = "data0"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)
    list0.append(value=data2)
    list0.append(value=data3)
    list0.append(value=data4)

    # Validation
    with pytest.raises(UnevenListLengthError):
        list0.opposite_unique(value=data1)


def test_opposite_thirteen_items_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data0"
    data2: str = "data0"
    data3: str = "data0"
    data4: str = "data0"
    data5: str = "data0"
    data6: str = "data0"
    data7: str = "data0"
    data8: str = "data0"
    data9: str = "data0"
    data10: str = "data0"
    data11: str = "data0"
    data12: str = "data0"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)
    list0.append(value=data2)
    list0.append(value=data3)
    list0.append(value=data4)
    list0.append(value=data5)
    list0.append(value=data6)
    list0.append(value=data7)
    list0.append(value=data8)
    list0.append(value=data9)
    list0.append(value=data10)
    list0.append(value=data11)
    list0.append(value=data12)

    # Validation
    with pytest.raises(UnevenListLengthError):
        list0.opposite_unique(value=data9)


def test_opposite_six_items_data_not_found_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)
    list0.append(value=data2)
    list0.append(value=data3)
    list0.append(value=data4)
    list0.append(value=data5)

    # Validation
    with pytest.raises(ValueNotFoundError):
        list0.opposite_unique(value=data)


def test_opposite_six_items_multiple_data_instances_found_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data"
    data5: str = "data5"

    list0: CDLL = CDLL()
    list0.append(value=data0)
    list0.append(value=data1)
    list0.append(value=data2)
    list0.append(value=data3)
    list0.append(value=data4)
    list0.append(value=data5)

    # Validation
    with pytest.raises(MultipleValuesFoundError):
        list0.opposite_unique(value=data)
