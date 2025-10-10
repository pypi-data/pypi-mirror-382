from src.py_cdll import CDLL


def test___init___data_list_empty_success():
    # Setup
    datas0: list = []

    # Execution
    list0: CDLL = CDLL(values=datas0)

    # Validation
    assert len(list0) == 0


def test___init___data_list_one_item_success():
    # Setup
    data0: str = "data0"
    datas0: list = [data0]

    # Execution
    list0: CDLL = CDLL(values=datas0)

    # Validation
    assert len(list0) == 1
    assert list0[0] == data0


def test___init___data_list_four_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list = [data0, data1, data2, data3]

    # Execution
    list0: CDLL = CDLL(values=datas0)

    # Validation
    assert len(list0) == 4
