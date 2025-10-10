from src.py_cdll import CDLL


def test_count_in_empty_failure():
    # Setup
    data: int = 1
    cdll0: CDLL = CDLL()
    count0: int = 0

    # Execution
    count1: int = cdll0.count(value=data)

    # Validation
    assert count0 == count1


def test_count_no_instance_among_single_success():
    # Setup
    data: int = 1
    data0: int = 0
    datas0: list[int] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    count0: int = 0

    # Execution
    count1: int = cdll0.count(value=data)

    # Validation
    assert count0 == count1


def test_count_one_instance_among_single_success():
    # Setup
    data: int = 1
    data0: int = 1
    datas0: list[int] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    count0: int = 1

    # Execution
    count1: int = cdll0.count(value=data)

    # Validation
    assert count0 == count1


def test_count_no_instance_among_multiple_success():
    # Setup
    data: int = 11
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    data5: int = 5
    datas0: list[int] = [data0, data1, data2, data3, data4, data5]
    cdll0: CDLL = CDLL(values=datas0)
    count0: int = 0

    # Execution
    count1: int = cdll0.count(value=data)

    # Validation
    assert count0 == count1


def test_count_one_instance_among_multiple_success():
    # Setup
    data: int = 1
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    data5: int = 5
    datas0: list[int] = [data0, data1, data2, data3, data4, data5]
    cdll0: CDLL = CDLL(values=datas0)
    count0: int = 1

    # Execution
    count1: int = cdll0.count(value=data)

    # Validation
    assert count0 == count1


def test_count_four_instances_among_multiple_success():
    # Setup
    data: int = 1
    data0: int = 0
    data1: int = 1
    data2: int = 1
    data3: int = 3
    data4: int = 1
    data5: int = 1
    datas0: list[int] = [data0, data1, data2, data3, data4, data5]
    cdll0: CDLL = CDLL(values=datas0)
    count0: int = 4

    # Execution
    count1: int = cdll0.count(value=data)

    # Validation
    assert count0 == count1
