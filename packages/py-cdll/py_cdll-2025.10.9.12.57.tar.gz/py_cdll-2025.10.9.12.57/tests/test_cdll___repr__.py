from re import match

from src.py_cdll import CDLL


def test___repr___empty_success():
    # Setup
    cdll0: CDLL = CDLL()
    repr0: str = r"^CDLL\(...\d{1,6}\)\[0, \[\]\]$"

    # Validation
    assert match(repr0, cdll0.__repr__()) is not None


def test___repr___text_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL[str] = CDLL(values=datas0)
    repr0: str = r"^CDLL\(...\d{1,6}\)\[3, \[" + f"'{data0}', '{data1}', '{data2}'" + r"\]\]$"

    # Execution
    repr1: str = cdll0.__repr__()

    # Validation
    assert match(repr0, repr1) is not None


def test___repr___int_success():
    # Setup
    data0: int = 0
    data1: int = 1
    data2: int = 2
    datas0: list[int] = [data0, data1, data2]
    cdll0: CDLL[int] = CDLL(values=datas0)
    repr0: str = r"^CDLL\(...\d{1,6}\)\[3, \[" + f"{data0}, {data1}, {data2}" + r"\]\]$"

    # Execution
    repr1: str = cdll0.__repr__()

    # Validation
    assert match(repr0, repr1) is not None


def test___repr___float_success():
    # Setup
    data0: float = 0.1
    data1: float = 1.2
    data2: float = 2.3
    datas0: list[float] = [data0, data1, data2]
    cdll0: CDLL[float] = CDLL(values=datas0)
    repr0: str = r"^CDLL\(...\d{1,6}\)\[3, \[" + f"{data0}, {data1}, {data2}" + r"\]\]$"

    # Execution
    repr1: str = cdll0.__repr__()

    # Validation
    assert match(repr0, repr1) is not None
