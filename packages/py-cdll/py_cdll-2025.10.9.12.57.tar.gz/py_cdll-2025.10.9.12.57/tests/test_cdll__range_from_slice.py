from src.py_cdll import CDLL


def test__indices_from_slice_first_last_single_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    cdll0: CDLL = CDLL(values=datas0)
    slice0: slice = slice(0, 10, 1)

    # Execution
    indices0: list[int] = list(cdll0._range_from_slice(segment=slice0))

    # Validation
    assert indices0 == datas0


def test__indices_from_slice_first_none_double_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [0, 2, 4, 6, 8]
    cdll0: CDLL = CDLL(values=datas0)
    slice0: slice = slice(0, None, 2)

    # Execution
    indices0: list[int] = list(cdll0._range_from_slice(segment=slice0))

    # Validation
    assert indices0 == datas1


def test__indices_from_slice_first_none_triple_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [0, 3, 6, 9]
    cdll0: CDLL = CDLL(values=datas0)
    slice0: slice = slice(0, None, 3)

    # Execution
    indices0: list[int] = list(cdll0._range_from_slice(segment=slice0))

    # Validation
    assert indices0 == datas1


def test__indices_from_slice_second_penultimate_quad_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = [1, 5]
    cdll0: CDLL = CDLL(values=datas0)
    slice0: slice = slice(1, 9, 4)

    # Execution
    indices0: list[int] = list(cdll0._range_from_slice(segment=slice0))

    # Validation
    assert indices0 == datas1


def test__indices_from_slice_last_none_none_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    datas1: list[int] = []
    cdll0: CDLL = CDLL(values=datas0)
    slice0: slice = slice(10, None, None)

    # Execution
    indices0: list[int] = list(cdll0._range_from_slice(segment=slice0))

    # Validation
    assert indices0 == datas1
