import pytest

from src.py_cdll import CDLL


def test___getitem___slice_single_item_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [3]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 3, 1)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_multiple_items_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [2, 3, 4]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(1, 4, None)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_single_item_last_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(4, 5, None)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_multiple_from_head_through_init_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(3, 5, None)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_multiple_items_spread_out_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [2, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(2, 7, 3)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_multiple_items_spread_out_less_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [0, 2, 4, 6, 8]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(0, None, 2)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_all_items_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1, 2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(0, None, None)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_all_items_away_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(5, None, None)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_no_items_with_index_out_of_range_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(37, None, None)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_zero_step_failure():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    cdll0: CDLL[int] = CDLL(values=datas0)
    slice0: slice = slice(None, None, 0)

    # Validation
    with pytest.raises(ValueError):
        _ = cdll0[slice0]


def test___getitem___slice_negative_two_step_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [4, 2]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(3, None, -2)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_out_of_range_step_from_zero_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = [1]
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(0, None, 11)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1


def test___getitem___slice_out_of_range_step_from_out_of_range_success():
    # Setup
    datas0: list[int] = [1, 2, 3, 4, 5]
    datas1: list[int] = []
    cdll0: CDLL[int] = CDLL(values=datas0)
    cdll1: CDLL[int] = CDLL(values=datas1)
    slice0: slice = slice(37, None, 11)

    # Execution
    cdll2: CDLL[int] = cdll0[slice0]

    # Validation
    assert cdll2 == cdll1
