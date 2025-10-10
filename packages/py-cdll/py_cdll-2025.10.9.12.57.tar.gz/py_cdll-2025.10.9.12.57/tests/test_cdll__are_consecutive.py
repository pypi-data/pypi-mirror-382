from src.py_cdll import CDLL


def test__are_consecutive_integers_consecutive_success():
    # Setup
    integers0: list[int] = [1, 2, 3, 4, 5]
    consecutive0: bool = True

    # Execution
    consecutive1: bool = CDLL._are_consecutive(numbers=integers0)

    # Validation
    assert consecutive0 == consecutive1


def test__are_consecutive_integers_not_consecutive_success():
    # Setup
    integers0: list[int] = [1, 4, 5]
    consecutive0: bool = False

    # Execution
    consecutive1: bool = CDLL._are_consecutive(numbers=integers0)

    # Validation
    assert consecutive0 == consecutive1
