from src.py_cdll import CDLL


def test_is_cdll_empty_zero_elements_success():
    # Setup
    cdll0: CDLL = CDLL()
    is_empty0: bool = True

    # Execution
    is_empty1: bool = cdll0.is_empty()

    # Validation
    assert is_empty1 is is_empty0


def test_is_cdll_empty_five_elements_success():
    # Setup
    datas0: list[int] = [0, 1, 2, 3, 4]
    cdll0: CDLL = CDLL(values=datas0)
    is_empty0: bool = False

    # Execution
    is_empty1: bool = cdll0.is_empty()

    # Validation
    assert is_empty1 is is_empty0
