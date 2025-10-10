import pytest

from src.py_cdll import CDLL


def test___radd___wrong_type_failure():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    adder0: int = 22

    # Validation
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        adder0 + cdll0


def test___radd___list_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=[])
    cdll2: CDLL = CDLL(values=datas0 + datas0)

    # Execution
    cdll3: CDLL = datas0 + cdll0

    # Validation
    assert cdll3 == cdll2
    assert cdll3 is not cdll0 and cdll3 is not cdll1 and cdll3 is not cdll2


def test___radd___empty_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=[])
    cdll2: CDLL = CDLL(values=datas0)

    # Execution
    cdll3: CDLL = [] + cdll0

    # Validation
    assert cdll3 == cdll2
    assert cdll3 is not cdll0 and cdll3 is not cdll1 and cdll3 is not cdll2


def test___radd___one_value_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data0, data1, data2]
    datas1: list[str] = [data3]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)
    cdll2: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll3: CDLL = datas1 + cdll0

    # Validation
    assert cdll3 == cdll2
    assert cdll3 is not cdll0 and cdll3 is not cdll1 and cdll3 is not cdll2


def test___radd___two_values_success():
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
    cdll2: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll3: CDLL = datas1 + cdll0

    # Validation
    assert cdll3 == cdll2
    assert cdll3 is not cdll0 and cdll3 is not cdll1 and cdll3 is not cdll2


def test___radd___five_values_success():
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
    cdll2: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll3: CDLL = datas1 + cdll0

    # Validation
    assert cdll3 == cdll2
    assert cdll3 is not cdll0 and cdll3 is not cdll1 and cdll3 is not cdll2


def test___radd___item_and_empty_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    datas1: list[str] = []
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll2: CDLL = datas1 + cdll0

    # Validation
    assert cdll2 == cdll1
    assert cdll2 is not cdll0 and cdll2 is not cdll1


def test___radd___empty_and_item_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = []
    datas1: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll2: CDLL = datas1 + cdll0
    # Validation
    assert cdll2 == cdll1
    assert cdll2 is not cdll0 and cdll2 is not cdll1


def test___radd___item_and_item_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    datas0: list[str] = [data0]
    datas1: list[str] = [data1]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll2: CDLL = datas1 + cdll0

    # Validation
    assert cdll2 == cdll1
    assert cdll2 is not cdll0 and cdll2 is not cdll1


def test___radd___two_items_and_five_items_success():
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
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll2: CDLL = datas1 + cdll0

    # Validation
    assert cdll2 == cdll1
    assert cdll2 is not cdll0 and cdll2 is not cdll1


def test___radd___three_items_and_four_items_success():
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
    cdll1: CDLL = CDLL(values=datas1 + datas0)

    # Execution
    cdll2: CDLL = datas1 + cdll0

    # Validation
    assert cdll2 == cdll1
    assert cdll2 is not cdll0 and cdll2 is not cdll1


def test___radd___cdll_tuple_success():
    # Setup
    cdll0: CDLL = CDLL()
    tuple1: tuple = tuple()

    # Execution
    cdll1: CDLL = tuple1 + cdll0

    # Validation
    assert cdll1 == cdll0
    assert cdll1 is not cdll0


def test___radd___cdll_list_success():
    # Setup
    cdll0: CDLL = CDLL()
    list1: list = list()

    # Execution
    cdll1: CDLL = list1 + cdll0

    # Validation
    assert cdll1 == cdll0
    assert cdll1 is not cdll0


def test___radd___cdll_set_success():
    # Setup
    cdll0: CDLL = CDLL()
    set1: set = set()

    # Execution
    cdll1: CDLL = set1 + cdll0

    # Validation
    assert cdll1 == cdll0
    assert cdll1 is not cdll0


def test___radd___cdll_range_success():
    # Setup
    cdll0: CDLL = CDLL(values=[5, 6, 7, 8, 9])
    cdll1: CDLL = CDLL(values=[0, 1, 2, 3, 4] + [5, 6, 7, 8, 9])
    range1: range = range(5)

    # Execution
    cdll2: CDLL = range1 + cdll0

    # Validation
    assert cdll2 == cdll1
