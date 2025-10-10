from src.py_cdll import CDLL


def test__slice_start_to_end_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data0)
    cdll1.append(data1)
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)

    slice0: slice = slice(None)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_inside_to_end_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)

    slice0: slice = slice(2, None)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_start_to_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data0)
    cdll1.append(data1)
    cdll1.append(data2)

    slice0: slice = slice(None, 3)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_inside_to_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data2)
    cdll1.append(data3)

    slice0: slice = slice(2, 4)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_outside_to_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(9, 3)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_inside_to_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)

    slice0: slice = slice(2, 9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_outside_to_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(7, 9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_inside_to_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data1)
    cdll1.append(data2)
    cdll1.append(data3)

    slice0: slice = slice(-4, 4)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_inside_to_negative_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data1)
    cdll1.append(data2)

    slice0: slice = slice(1, -2)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_inside_to_negative_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data2)
    cdll1.append(data3)

    slice0: slice = slice(-3, -1)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_outside_to_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data0)
    cdll1.append(data1)
    cdll1.append(data2)

    slice0: slice = slice(-9, 3)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_inside_to_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data1)
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)

    slice0: slice = slice(-4, 9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_outside_to_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data0)
    cdll1.append(data1)
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)

    slice0: slice = slice(-9, 9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_outside_to_negative_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(9, -4)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_inside_to_negative_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(2, -9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_outside_to_negative_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(9, -9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_outside_to_negative_inside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()
    cdll1.append(data0)
    cdll1.append(data1)

    slice0: slice = slice(-9, -3)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_inside_to_negative_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(-3, -9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2


def test__slice_negative_outside_to_negative_outside_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    cdll1: CDLL = CDLL()

    slice0: slice = slice(-6, -9)

    # Execution
    cdll2: CDLL = cdll0._slice(segment=slice0)

    # Validation
    assert cdll1 == cdll2
