from typing import Iterator

from src.py_cdll import CDLL
from src.py_cdll.node import Node


def test__nodes_index_empty_nodes_empty_indices_success():
    # Setup
    indices0: list[int] = []
    cdll0: CDLL = CDLL()

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_index(indices=indices0)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_index_empty_nodes_five_indices_success():
    # Setup
    indices0: list[int] = [2, 3, 6, 9, 14]
    cdll0: CDLL = CDLL()

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_index(indices=indices0)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_index_four_nodes_empty_indices_success():
    # Setup
    indices0: list[int] = []
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list[str] = [data0, data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_index(indices=indices0)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_index_seven_nodes_three_indices_success():
    # Setup
    indices0: list[int] = [2, 3, 6]
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    datas0: list[str] = [data0, data1, data2, data3, data4, data5, data6]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_index(indices=indices0)

    # Validation
    assert len(list(iterator0)) == 3


def test__nodes_index_seven_nodes_five_repeated_indices_success():
    # Setup
    indices0: list[int] = [2, 3, 3, 6, 6]
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    datas0: list[str] = [data0, data1, data2, data3, data4, data5, data6]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_index(indices=indices0)

    # Validation
    assert len(list(iterator0)) == 5


def test__nodes_index_seven_nodes_three_indices_also_out_of_range_success():
    # Setup
    indices0: list[int] = [2, 11, 37]
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    datas0: list[str] = [data0, data1, data2, data3, data4, data5, data6]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_index(indices=indices0)

    # Validation
    assert len(list(iterator0)) == 1
