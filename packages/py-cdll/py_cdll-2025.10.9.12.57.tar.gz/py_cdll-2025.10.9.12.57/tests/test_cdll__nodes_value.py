from typing import Iterator

from src.py_cdll import CDLL
from src.py_cdll.compare import Comparison
from src.py_cdll.node import Node


def test__nodes_value_zero_yields_zero_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    cdll0: CDLL = CDLL()
    cdll0.append(value=data0)
    cdll0.append(value=data1)
    cdll0.append(value=data2)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value(value=data, comparison=Comparison.IDENTITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_one_yields_one_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    cdll0: CDLL = CDLL()
    cdll0.append(value=data0)
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll0.append(value=data)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value(value=data, comparison=Comparison.IDENTITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_three_yields_three_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    cdll0: CDLL = CDLL()
    cdll0.append(value=data)
    cdll0.append(value=data0)
    cdll0.append(value=data1)
    cdll0.append(value=data)
    cdll0.append(value=data2)
    cdll0.append(value=data)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value(value=data, comparison=Comparison.IDENTITY)

    # Validation
    assert len(list(iterator0)) == 3


def test__nodes_value_three_yields_three_indices_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    cdll0: CDLL = CDLL()
    cdll0.append(value=data)
    cdll0.append(value=data0)
    cdll0.append(value=data1)
    cdll0.append(value=data)
    cdll0.append(value=data2)
    cdll0.append(value=data)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value(value=data, comparison=Comparison.IDENTITY)

    # Validation
    assert next(iterator0) == cdll0._head
    assert next(iterator0) == cdll0._head.next.next.next
    assert next(iterator0) == cdll0._head.next.next.next.next.next
