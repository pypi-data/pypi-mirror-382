from src.py_cdll import CDLL


def test___len___empty_list_success():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    assert len(cdll0) == 0


def test___len___with_one_item_success():
    # Setup
    cdll0: CDLL = CDLL(values=["data"])

    # Validation
    assert len(cdll0) == 1


def test___len___with_six_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    datas0: list[str] = [data0, data1, data2, data3, data4, data5]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    assert len(cdll0) == 6


def test___len___with_111_items_success():
    # Setup
    amount: int = 111
    data: range = range(amount)
    cdll0: CDLL = CDLL(values=data)

    # Validation
    assert len(cdll0) == amount
