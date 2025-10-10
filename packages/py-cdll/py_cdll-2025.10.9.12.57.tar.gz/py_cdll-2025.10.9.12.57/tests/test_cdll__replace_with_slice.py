import pytest

from src.py_cdll import CDLL


def test__replace_with_slice_replace_single_empty_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 4, 5]
    datas2: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 3, 1)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_multiple_empty_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 5]
    datas2: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(1, 4, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_single_in_middle_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 333, 4, 5]
    datas2: list[int] = [333]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 3, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_multiple_in_middle_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 222, 23, 333, 34, 444, 5]
    datas2: list[int] = [222, 23, 333, 34, 444]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(1, 4, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_single_in_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 555]
    datas2: list[int] = [555]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(4, 5, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_multiple_from_tail_past_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 444, 555, 666, 777, 888]
    datas2: list[int] = [444, 555, 666, 777, 888]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(3, 5, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_multiple_spread_out_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [0, 1, 222, 3, 4, 555, 6, 7, 8, 9]
    datas2: list[int] = [222, 555]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 7, 3)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_replace_multiple_spread_out_with_too_few_replacement_values_failure():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas2: list[int] = [111, 222, 333]
    cdll0: CDLL[int] = CDLL(values=datas0)
    slice0: slice = slice(0, None, 2)

    # Validation
    with pytest.raises(ValueError):
        cdll0._replace_with_slice(segment=slice0, values=datas2)


def test__replace_with_slice_replace_multiple_spread_out_with_too_many_replacement_values_failure():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas2: list[int] = [111, 222, 333, 444, 555, 666]
    cdll0: CDLL[int] = CDLL(values=datas0)
    slice0: slice = slice(0, None, 2)

    # Validation
    with pytest.raises(ValueError):
        cdll0._replace_with_slice(segment=slice0, values=datas2)


def test__replace_with_slice_replace_all_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [111, 222, 333, 444, 555]
    datas2: list[int] = [111, 222, 333, 444, 555]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(0, None, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_add_nothing_to_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5]
    datas2: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(5, None, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_add_single_to_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5, 666]
    datas2: list[int] = [666]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(5, None, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_add_single_to_last_with_high_index_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5, 666]
    datas2: list[int] = [666]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(555, None, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1


def test__replace_with_slice_add_multiple_to_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5, 666, 777, 888, 999]
    datas2: list[int] = [666, 777, 888, 999]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(5, None, None)

    # Execution
    cdll0._replace_with_slice(segment=slice0, values=datas2)

    # Validation
    assert cdll0 == cdll1
