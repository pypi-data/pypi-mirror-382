from typing import Iterator, Any

import pytest

from src.py_cdll import CDLL


def test___reversed___empty_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Execution
    iterator0: Iterator[Any] = reversed(cdll0)

    # Validation
    with pytest.raises(StopIteration):
        next(iterator0)


def test___reversed___one_yields_one_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Any] = reversed(cdll0)

    # Validation
    assert len(list(iterator0)) == 1


def test___reversed___three_yields_three_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Any] = reversed(cdll0)

    # Validation
    assert len(list(iterator0)) == 3


def test___reversed___three_yields_three_index_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Any] = reversed(cdll0)

    # Validation
    assert next(iterator0) == data2
    assert next(iterator0) == data1
    assert next(iterator0) == data0
