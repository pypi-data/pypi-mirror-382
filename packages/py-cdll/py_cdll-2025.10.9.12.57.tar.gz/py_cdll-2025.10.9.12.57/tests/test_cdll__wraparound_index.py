import pytest

from src.py_cdll import CDLL


def test__wraparound_index_length_zero_index_one_failure():
    # Setup
    datas0: list = []
    cdll0: CDLL = CDLL(values=datas0)
    index0: int = 1

    # Validation
    with pytest.raises(ZeroDivisionError):
        cdll0._wraparound_index(index=index0)


def test__wraparound_index_length_one_index_six_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL[str] = CDLL(values=datas0)
    index0: int = 6
    index1: int = 0

    # Execution
    index2: int = cdll0._wraparound_index(index=index0)

    # Validation
    assert index2 == index1


def test__wraparound_index_length_two_index_thirty_seven_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    datas0: list[str] = [data0, data1]
    cdll0: CDLL[str] = CDLL(values=datas0)
    index0: int = 37
    index1: int = 1

    # Execution
    index2: int = cdll0._wraparound_index(index=index0)

    # Validation
    assert index2 == index1


def test__wraparound_index_length_three_index_minus_five_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL[str] = CDLL(values=datas0)
    index0: int = -5
    index1: int = 1

    # Execution
    index2: int = cdll0._wraparound_index(index=index0)

    # Validation
    assert index2 == index1


def test__wraparound_index_length_four_index_minus_one_hundred_twenty_seven_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data0, data1, data2, data3]
    cdll0: CDLL[str] = CDLL(values=datas0)
    index0: int = -127
    index1: int = 1

    # Execution
    index2: int = cdll0._wraparound_index(index=index0)

    # Validation
    assert index2 == index1


def test__wraparound_index_length_five_index_ten_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL[str] = CDLL(values=datas0)
    index0: int = 10
    index1: int = 0

    # Execution
    index2: int = cdll0._wraparound_index(index=index0)

    # Validation
    assert index2 == index1
