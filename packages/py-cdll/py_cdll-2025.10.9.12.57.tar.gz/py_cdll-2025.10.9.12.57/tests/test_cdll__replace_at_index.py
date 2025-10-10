import pytest

from src.py_cdll import CDLL


def test__replace_at_index_empty_cdll_index_zero_failure():
    # Setup
    index0: int = 0
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0._replace_at_index(index=index0, replacement=data0)


def test__replace_at_index_empty_cdll_index_seven_failure():
    # Setup
    index0: int = 7
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0._replace_at_index(index=index0, replacement=data0)


def test__replace_at_index_length_three_cdll_index_zero_success():
    # Setup
    index0: int = 0
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll0._replace_at_index(index=index0, replacement=data0)

    # Validation
    assert cdll0[index0] == data0


def test__replace_at_index_length_three_cdll_index_six_failure():
    # Setup
    index0: int = 7
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(IndexError):
        cdll0._replace_at_index(index=index0, replacement=data0)


def test__replace_at_index_zero_with_empty_list_failure():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0[0] = data0


def test__replace_at_index_with_empty_list_failure():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0[2] = data0


def test__replace_at_index_greater_than_list_length_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(data1)

    # Validation
    with pytest.raises(IndexError):
        cdll0[2] = data0


def test__replace_at_index_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    data_new1: str = "inserted1"
    data_new2: str = "inserted2"
    cdll0[2] = data_new1
    cdll0[3] = data_new2

    # Validation
    assert cdll0[0] == data0
    assert cdll0[1] == data1
    assert cdll0[2] == data_new1
    assert cdll0[3] == data_new2
    assert len(cdll0) == 4


def test__replace_at_index_zero_updates_head_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data_new: str = "new_head"
    cdll0: CDLL = CDLL(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)

    # Execution
    cdll0[0] = data_new

    # Validation
    assert cdll0.head == data_new


def test__replace_at_index_zero_of_empty_list_failure():
    # Setup
    data: str = "data"
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0[0] = data
