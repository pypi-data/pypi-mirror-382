from typing import Iterator

import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import Node


def test__nodes_empty_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Execution
    # iterator0: Iterator[tuple[int, Node]] = cdll0._nodes()
    iterator0: Iterator[Node] = cdll0._nodes()

    # Validation
    with pytest.raises(StopIteration):
        next(iterator0)


def test__nodes_one_yields_one_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    # iterator0: Iterator[tuple[int, Node]] = cdll0._nodes()
    iterator0: Iterator[Node] = cdll0._nodes()

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_three_yields_three_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes()

    # Validation
    assert len(list(iterator0)) == 3


def test__nodes_three_yields_three_index_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes()

    # Validation
    assert next(iterator0).value == data0
    assert next(iterator0).value == data1
    assert next(iterator0).value == data2
