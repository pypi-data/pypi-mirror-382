import pytest

from src.py_cdll import CDLL


def test___iadd___wrong_type_failure():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    adder0: int = 22

    # Validation
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        cdll0 += adder0


def test___iadd___list_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas0 + datas0)
    cdll2: CDLL = cdll0

    # Execution
    cdll0 += datas0

    # Validation
    assert cdll1 == cdll0
    assert cdll2 is cdll0


def test___iadd___empty_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas0)
    cdll2: CDLL = cdll0

    # Execution
    cdll0 += []

    # Validation
    assert cdll1 == cdll0
    assert cdll2 is cdll0


def test___iadd___one_value_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data0, data1, data2]
    datas1: list[str] = [data3]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0 + datas1)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___two_values_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2]
    datas1: list[str] = [data3, data4]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0 + datas1)
    cdll3: CDLL = cdll0

    # Execution
    # cdll3: CDLL = (
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___five_values_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    data7: str = "data7"
    datas0: list[str] = [data0, data1, data2]
    datas1: list[str] = [data3, data4, data5, data6, data7]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0 + datas1)
    cdll3: CDLL = cdll0

    # Execution
    # cdll3: CDLL =
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___item_and_empty_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    datas1: list[str] = []
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___empty_and_item_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = []
    datas1: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas1)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___item_and_item_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    datas0: list[str] = [data0]
    datas1: list[str] = [data1]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0 + datas1)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___two_items_and_five_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    datas0: list[str] = [data0, data1]
    datas1: list[str] = [data2, data3, data4, data5, data6]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0 + datas1)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___three_items_and_four_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    datas0: list[str] = [data0, data1, data2]
    datas1: list[str] = [data3, data4, data5, data6]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas0 + datas1)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += cdll1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___cdll_tuple_success():
    # Setup
    cdll0: CDLL = CDLL()
    tuple1: tuple = tuple()
    cdll2: CDLL = CDLL()
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += tuple1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___cdll_list_success():
    # Setup
    cdll0: CDLL = CDLL()
    list1: list = list()
    cdll2: CDLL = CDLL()
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += list1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___cdll_set_success():
    # Setup
    cdll0: CDLL = CDLL()
    set1: set = set()
    cdll2: CDLL = CDLL()
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += set1

    # Validation
    assert cdll2 == cdll0
    assert cdll3 is cdll0


def test___iadd___cdll_range_success():
    # Setup
    cdll0: CDLL = CDLL()
    cdll1: CDLL = CDLL(values=[0, 1, 2, 3, 4])
    range1: range = range(5)
    cdll3: CDLL = cdll0

    # Execution
    cdll0 += range1

    # Validation
    assert cdll1 == cdll0
    assert cdll3 is cdll0
