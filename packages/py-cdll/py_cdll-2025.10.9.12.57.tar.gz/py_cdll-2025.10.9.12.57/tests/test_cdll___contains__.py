from src.py_cdll import CDLL


def test___contains___empty_cdll_success():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL()

    # Execution
    bool0: bool = data0 in cdll0

    # Validation
    assert bool0 is False


def test___contains___data_not_in_cdll_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])

    # Execution
    bool0: bool = data1 in cdll0

    # Validation
    assert bool0 is False


def test___contains___data_in_cdll_success():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL(values=[data0])

    # Execution
    bool0: bool = data0 in cdll0

    # Validation
    assert bool0 is True
