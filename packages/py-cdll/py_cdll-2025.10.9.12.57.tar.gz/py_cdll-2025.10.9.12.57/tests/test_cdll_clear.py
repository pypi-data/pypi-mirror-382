from src.py_cdll import CDLL


def test_clear_empty_list_success():
    # Setup
    cdll0: CDLL = CDLL()

    # Execution
    cdll0.clear()

    # Validation
    assert len(cdll0) == 0
    assert cdll0._head is None


def test_clear_list_with_content_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll0.clear()

    # Validation
    assert len(cdll0) == 0
    assert cdll0._head is None
