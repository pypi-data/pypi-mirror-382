import pytest

from src.py_cdll import CDLL


def test___delitem___slice_single_empty_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 3, 1)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_multiple_empty_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(1, 4, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_single_in_middle_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 3, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_multiple_in_middle_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(1, 4, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_single_from_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(4, 5, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_multiple_from_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(3, 5, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_multiple_spread_out_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [0, 1, 3, 4, 6, 7, 8, 9]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 7, 3)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_all_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(0, None, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_nothing_after_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(5, None, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_nothing_after_last_with_high_index_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(555, None, None)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_zero_step_failure():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    slice0: slice = slice(None, None, 0)

    # Validation
    with pytest.raises(ValueError):
        del cdll0[slice0]


def test___delitem___slice_negative_two_step_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 3, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(3, None, -2)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_out_of_range_step_from_zero_to_out_of_range_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(0, None, 11)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1


def test___delitem___slice_out_of_range_step_from_out_of_range_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(37, None, 11)

    # Execution
    del cdll0[slice0]

    # Validation
    assert cdll0 == cdll1
