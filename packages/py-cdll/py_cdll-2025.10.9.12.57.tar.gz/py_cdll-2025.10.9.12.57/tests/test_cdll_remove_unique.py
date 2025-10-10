import pytest

from src.py_cdll import CDLL, EmptyCDLLError, MultipleValuesFoundError, ValueNotFoundError


def test_remove_unique_empty_cdll_failure():
    # Setup
    data: str = "data"
    cdll0: CDLL = CDLL()

    # Execution
    with pytest.raises(EmptyCDLLError):
        cdll0.remove_unique(value=data)


def test_remove_unique_single_instance_among_single_success():
    # Setup
    data: str = "data"
    data0: str = "data"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll0.remove_unique(value=data)

    # Verification
    assert len(cdll0) == 0


def test_remove_unique_single_instance_among_multiple_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    cdll0.remove_unique(value=data)

    # Verification
    assert data not in cdll0


def test_remove_unique_multiple_instances_among_multiple_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data"
    data2: str = "data2"
    data3: str = "data"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Verification
    with pytest.raises(MultipleValuesFoundError):
        cdll0.remove_unique(value=data)


def test_remove_unique_no_instances_among_multiple_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Verification
    with pytest.raises(ValueNotFoundError):
        cdll0.remove_unique(value=data)
