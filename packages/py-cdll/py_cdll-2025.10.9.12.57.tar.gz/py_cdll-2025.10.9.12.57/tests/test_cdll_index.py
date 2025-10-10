import pytest

from src.py_cdll import CDLL


def test_index_with_empty_list_failure():
    # Setup
    data0: str = "data0"
    list0: CDLL = CDLL()

    # Validation
    with pytest.raises(ValueError):
        list0.index(value=data0)


def test_index_single_element_single_hit_success():
    # Setup
    data0: str = "data0"
    datas0: list[str] = [data0]
    list0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = list0.index(value=data0)

    # Validation
    assert index0 == 0


def test_index_multiple_elements_single_hit_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    list0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = list0.index(value=data0)

    # Validation
    assert index0 == 0


def test_index_multiple_elements_no_hits_failure():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    list0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueError):
        list0.index(value=data)


def test_index_multiple_elements_multiple_hits_success():
    # Setup
    data: str = "data"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data, data1, data, data2]
    list0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = list0.index(value=data)

    # Validation
    assert index0 == 1


def test_index_found_value_stop_out_of_range_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = cdll0.index(value=data1, stop=len(cdll0) + 1)

    # Validation
    assert index0 == 1


def test_index_not_found_value_stop_out_of_range_failure():
    # Setup
    value0: str = "data5"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=value0, stop=len(cdll0) + 5)


def test_index_found_value_in_range_stop_mid_list_success():
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
    index0: int = cdll0.index(value=data2, stop=len(cdll0) // 2)

    # Validation
    assert index0 == 2


def test_index_not_found_value_out_of_range_stop_mid_list_success():
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

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=data4, stop=len(cdll0) // 2)


def test_index_not_found_value_unavailable_stop_mid_list_success():
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

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=value0, stop=len(cdll0) // 2)


def test_index_found_value_in_range_start_mid_list_success():
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
    index0: int = cdll0.index(value=data5, start=len(cdll0) // 2)

    # Validation
    assert index0 == 5


def test_index_not_found_value_out_of_range_start_mid_list_success():
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

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=data2, start=len(cdll0) // 2)


def test_index_not_found_value_unavailable_start_mid_list_success():
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

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=value0, start=len(cdll0) // 2)


def test_index_not_found_value_out_of_range_slice_zero_length_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=data1, start=1, stop=1)


def test_index_not_found_value_unavailable_slice_zero_length_success():
    # Setup
    value0: str = "data6"
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=datas0)

    # Validation
    with pytest.raises(ValueError):
        cdll0.index(value=value0, start=2, stop=2)


def test_index_value_found_slice_start_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = cdll0.index(value=data2, start=-3, stop=3)

    # Validation
    assert index0 == 2


def test_index_value_found_slice_stop_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = cdll0.index(value=data2, start=2, stop=-2)

    # Validation
    assert index0 == 2


def test_index_value_found_slice_both_negative_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    datas0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=datas0)

    # Execution
    index0: int = cdll0.index(value=data2, start=-3, stop=-2)

    # Validation
    assert index0 == 2
