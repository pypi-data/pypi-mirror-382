import pytest

from src.py_cdll import CDLL, InputNotIterableError


def test_extend_input_empty_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list = []
    datas1: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas1)
    cdll1: CDLL = CDLL(values=datas1)

    # Execution
    cdll0.extend(values=datas0)

    # Validation
    assert cdll0 == cdll1


def test_extend_input_one_item_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data3]
    datas1: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas1)
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll0.extend(values=datas0)

    # Validation
    assert cdll0 == cdll1


def test_extend_input_six_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    datas0: list[str] = [data6]
    datas1: list[str] = [data0, data1, data2, data3, data4, data5]
    cdll0: CDLL = CDLL(values=datas1)
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll0.extend(values=datas0)

    # Validation
    assert cdll0 == cdll1


def test_extend_input_non_valid_failure():
    # Setup
    data0: int = 9
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    datas1: list[str] = [data0, data1, data2, data3, data4, data5]
    cdll0: CDLL = CDLL(values=datas1)

    # Validation
    with pytest.raises(InputNotIterableError):
        # noinspection PyTypeChecker
        cdll0.extend(values=data0)
