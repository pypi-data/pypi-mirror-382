import pytest

from src.py_cdll import CDLL, ValueNotFoundError, EmptyCDLLError
from src.py_cdll.compare import Comparison
from src.py_cdll.node import Node


def test__node_first_single_option_single_hit_identity_success():
    # Setup
    index0: int = 0
    data0: str = "data0"
    datas0: list[str] = [data0]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    # index1, node0 = cdll0._node_first(value=data0, comparison=Comparison.IDENTITY)
    node0 = cdll0._node_first(value=data0, comparison=Comparison.IDENTITY)

    # Validation
    # assert index0 == index1
    assert index0 == node0.index
    assert data0 is node0.value


def test__node_first_single_option_single_hit_equality_success():
    # Setup
    index0: int = 0
    data0: str = "data0"
    data1: str = "data0"
    datas0: list[str] = [data1]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    # index1, node0 = cdll0._node_first(value=data0, comparison=Comparison.EQUALITY)
    node0 = cdll0._node_first(value=data0, comparison=Comparison.EQUALITY)

    # Validation
    # assert index0 == index1
    assert index0 == node0.index
    assert data0 == node0.value


def test__node_first_multiple_options_multiple_equal_single_hit_identity_success():
    # Setup
    index0: int = 2
    data0: list[str] = ["data0"]
    data1: list[str] = ["data0"]
    data2: list[str] = ["data0"]
    datas0: list[list[str]] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_first(value=data2, comparison=Comparison.IDENTITY)

    # Validation
    assert index0 == node0.index
    assert data2 is node0.value


def test__node_first_multiple_options_single_hit_equality_success():
    # Setup
    index0: int = 3
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data0"
    datas0: list[str] = [data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_first(value=data0, comparison=Comparison.EQUALITY)

    # Validation
    assert index0 == node0.index
    assert data0 == node0.value


def test__node_first_multiple_options_first_hit_identity_success():
    # Setup
    index0: int = 1
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data0"
    datas0: list[str] = [data1, data0, data2, data3, data0, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_first(value=data0, comparison=Comparison.IDENTITY)

    # Validation
    assert index0 == node0.index
    assert data0 == node0.value


def test__node_first_multiple_options_first_hit_equality_failure():
    # Setup
    index0: int = 1
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data0"
    datas0: list[str] = [data1, data4, data2, data3, data4, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    node0: Node = cdll0._node_first(value=data0, comparison=Comparison.EQUALITY)

    # Validation
    assert index0 == node0.index
    assert data0 == node0.value


def test__node_first_no_options_no_hits_failure():
    # Setup
    data0: str = "data0"
    datas0: list = []
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(EmptyCDLLError):
        cdll0._node_first(value=data0, comparison=Comparison.IDENTITY)


def test__node_first_single_option_no_hits_identity_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    datas0: list = [data1]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueNotFoundError):
        cdll0._node_first(value=data0, comparison=Comparison.IDENTITY)


def test__node_first_single_option_no_hits_equality_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    datas0: list = [data1]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueNotFoundError):
        cdll0._node_first(value=data0, comparison=Comparison.EQUALITY)


def test__node_first_multiple_options_no_hits_identity_failure():
    # Setup
    data0: list[str] = ["data0"]
    data1: list[str] = ["data1"]
    data2: list[str] = ["data2"]
    data3: list[str] = ["data0"]
    datas0: list[list[str]] = [data1, data3, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueNotFoundError):
        cdll0._node_first(value=data0, comparison=Comparison.IDENTITY)


def test__node_first_multiple_options_no_hits_equality_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    datas0: list = [data1, data2, data3]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueNotFoundError):
        cdll0._node_first(value=data0, comparison=Comparison.EQUALITY)
