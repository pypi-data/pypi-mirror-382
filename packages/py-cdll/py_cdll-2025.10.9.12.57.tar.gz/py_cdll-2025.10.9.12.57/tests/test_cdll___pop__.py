import pytest

from src.py_cdll import CDLL


def test___pop___empty_cdll_failure():
    # Setup
    index: int = 0
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0.pop(index=index)


def test___pop___index_outside_multiple_elements_range_failure():
    # Setup
    index: int = 9
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(IndexError):
        cdll0.pop(index=index)


def test___pop___index_inside_single_elements_success():
    # Setup
    index: int = 0
    data: str = "data"
    data0: str = "data"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    data1: str = cdll0.pop(index=index)

    # Validation
    assert data == data1


def test___pop___default_index_success():
    # Setup
    data0: str = "data"
    data1: str = "data"
    data2: str = "data"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    data3: str = cdll0.pop()

    # Validation
    assert data3 == data2


def test___pop___index_inside_multiple_elements_success():
    # Setup
    index: int = 3
    data: str = "data3"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    data1: str = cdll0.pop(index=index)

    # Validation
    assert data == data1
