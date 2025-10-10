import pytest

from src.py_cdll import CDLL


def test___mul___zero_empty_success():
    # Setup
    multiplier0: int = 0

    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]

    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL()

    # Execution
    cdll2: CDLL = cdll0 * multiplier0

    # Validation
    assert cdll1 == cdll2
    assert cdll2 is not cdll0


def test___mul___one_same_success():
    # Setup
    multiplier0: int = 1

    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]

    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas0)

    # Execution
    cdll2: CDLL = cdll0 * multiplier0

    # Validation
    assert cdll1 == cdll2
    assert cdll2 is not cdll0


def test___mul___two_double_success():
    # Setup
    multiplier0: int = 2

    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]

    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas0 + datas0)

    # Execution
    cdll2: CDLL = cdll0 * multiplier0

    # Validation
    assert cdll1 == cdll2
    assert cdll2 is not cdll0


def test___mul___five_quintuple_success():
    # Setup
    multiplier0: int = 5

    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]

    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas0 + datas0 + datas0 + datas0 + datas0)

    # Execution
    cdll2: CDLL = cdll0 * multiplier0

    # Validation
    assert cdll1 == cdll2
    assert cdll2 is not cdll0


def test___mul___minus_one_empty_success():
    # Setup
    multiplier0: int = -1

    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]

    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL()

    # Execution
    cdll2: CDLL = cdll0 * multiplier0

    # Validation
    assert cdll1 == cdll2
    assert cdll2 is not cdll0


def test___mul___non_integer_failure():
    # Setup
    multiplier0: float = 3.7

    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]

    cdll0: CDLL = CDLL(datas0)

    # Validation
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        cdll0 * multiplier0
