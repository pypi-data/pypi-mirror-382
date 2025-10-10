from src.py_cdll import CDLL


def test__head_empty_success():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    assert cdll0._head is None


def test__head_three_items_success():
    # Setup
    data0: int = 0
    data1: int = 1
    data2: int = 2
    datas0: list[int] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    assert cdll0._head.previous is cdll0._head.next.next
    assert cdll0._head.previous.previous is cdll0._head.next
    assert cdll0._head.previous.previous.previous is cdll0._head
    assert cdll0._head.next.next.next is cdll0._head
