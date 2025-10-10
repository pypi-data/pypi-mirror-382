from typing import Iterator

from src.py_cdll import CDLL
from src.py_cdll.compare import Comparison
from src.py_cdll.node import Node


def test__nodes_value_constrained_zero_yields_zero_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_one_yields_one_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2, data]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_constrained_three_yields_three_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data, data0, data1, data, data2, data]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data, comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 3


def test__nodes_value_constrained_three_yields_three_indices_success():
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data, comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert next(iterator0) == cdll0._head
    assert next(iterator0) == cdll0._head.next.next.next
    assert next(iterator0) == cdll0._head.next.next.next.next.next


def test__nodes_value_constrained_found_value_stop_out_of_range_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data1,
                                                                           stop=len(cdll0) + 1,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_constrained_not_found_value_stop_out_of_range_success():
    # Setup
    value0: str = "data5"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=value0,
                                                                           stop=len(cdll0) + 5,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_found_value_in_range_stop_mid_list_success():
    # Setup
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data2,
                                                                           stop=len(cdll0) // 2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_constrained_not_found_value_out_of_range_stop_mid_list_success():
    # Setup
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data4,
                                                                           stop=len(cdll0) // 2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_not_found_value_unavailable_stop_mid_list_success():
    # Setup
    value0: str = "data9"
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=value0,
                                                                           stop=len(cdll0) // 2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_found_value_in_range_start_mid_list_success():
    # Setup
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data5,
                                                                           start=len(cdll0) // 2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_constrained_not_found_value_out_of_range_start_mid_list_success():
    # Setup
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data2,
                                                                           start=len(cdll0) // 2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_not_found_value_unavailable_start_mid_list_success():
    # Setup
    value0: str = "data9"
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
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=value0,
                                                                           start=len(cdll0) // 2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_not_found_value_out_of_range_slice_zero_length_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data1,
                                                                           start=1,
                                                                           stop=1,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_not_found_value_unavailable_slice_zero_length_success():
    # Setup
    value0: str = "data6"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=value0,
                                                                           start=2,
                                                                           stop=2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 0


def test__nodes_value_constrained_value_found_slice_start_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data2,
                                                                           start=-3,
                                                                           stop=3,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_constrained_value_found_slice_stop_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data2,
                                                                           start=2,
                                                                           stop=-2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1


def test__nodes_value_constrained_value_found_slice_both_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    iterator0: Iterator[Node] = cdll0._nodes_value_constrained(value=data2,
                                                                           start=-3,
                                                                           stop=-2,
                                                                           comparison=Comparison.IDENTITY_OR_EQUALITY)

    # Validation
    assert len(list(iterator0)) == 1
