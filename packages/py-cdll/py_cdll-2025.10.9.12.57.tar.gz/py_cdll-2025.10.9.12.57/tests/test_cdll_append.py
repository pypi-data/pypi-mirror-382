from src.py_cdll import CDLL


def test_append_to_end_of_empty_list_success():
    # Setup
    data: str = "data"
    cdll0: CDLL = CDLL()

    # Execution
    cdll0.append(value=data)

    # Validation
    assert cdll0.head == data
    assert cdll0.last == data


def test_append_to_end_of_list_success():
    # Setup
    head: str = "head"
    data: str = "data"
    cdll0: CDLL = CDLL(values=[head])

    # Execution
    cdll0.append(data)

    # Validation
    assert cdll0.head == head
    assert cdll0.last == data


def test_append_retrieval_success():
    # Setup
    head: str = "head"
    data1: str = "data1"
    data2: str = "data2"
    cdll0: CDLL = CDLL(values=[head])

    # Execution
    cdll0.append(data1)
    cdll0.append(data2)

    # Validation
    assert cdll0.head == head
    assert cdll0.last == data2
    assert cdll0[0] == head
    assert cdll0[1] == data1
    assert cdll0[2] == data2
