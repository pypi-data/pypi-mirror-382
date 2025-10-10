from copy import copy

from src.py_cdll import CDLL


def test___copy___empty_success():
    # Setup
    cdll0: CDLL = CDLL()

    # Execution
    cdll1: CDLL = copy(cdll0)

    # Validation
    assert cdll0 is not cdll1
    assert cdll0 == cdll1


def test___copy___single_value_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll1: CDLL = copy(cdll0)

    # Validation
    assert cdll0 is not cdll1
    assert cdll0 == cdll1


def test___copy___multiple_values_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll1: CDLL = copy(cdll0)

    # Validation
    assert cdll0 is not cdll1
    assert cdll0 == cdll1
