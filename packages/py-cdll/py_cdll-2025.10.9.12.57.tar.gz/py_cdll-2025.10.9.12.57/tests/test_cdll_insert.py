from src.py_cdll import CDLL


def test_insert_with_empty_list_success():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL()
    index_requested: int = 2
    index_inserted: int = 0

    # Execution
    cdll0.insert(index=index_requested, value=data0)

    # Validation
    assert cdll0[index_inserted] == data0


def test_insert_after_last_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1]
    cdll0: CDLL = CDLL(values=datas0)
    index_requested: int = 2

    # Execution
    cdll0.insert(index=index_requested, value=data2)

    # Validation
    assert cdll0.last == data2


def test_insert_way_out_of_range_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1]
    cdll0: CDLL = CDLL(values=datas0)
    index_requested: int = 222
    index_inserted: int = 2

    # Execution
    cdll0.insert(index=index_requested, value=data2)

    # Validation
    assert cdll0[index_inserted] == data2


def test_insert_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll0.insert(index=2, value=data4)

    # Validation
    assert cdll0[3] == data2


def test_insert_index_zero_in_empty_list_success():
    # Setup
    index0: int = 0
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Execution
    cdll0._insert(index=index0, value=data0)

    # Validation
    assert cdll0[0] == data0


def test_insert_index_seven_in_empty_list_success():
    # Setup
    index0: int = 7
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Execution
    cdll0._insert(index=index0, value=data0)

    # Validation
    assert cdll0[0] == data0


def test_insert_index_zero_update_head_next_prev_connections_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll0._insert(index=0, value=data5)

    # Validation
    assert cdll0.head == data5
    assert cdll0._head.next.value == data0
    assert cdll0._head.previous.value == data4
    assert cdll0._head.next.previous.value == data5
    assert cdll0._head.previous.next.value == data5
