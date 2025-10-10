from re import match

from src.py_cdll import CDLL


def test___str___empty_success():
    # Setup
    cdll0: CDLL = CDLL()
    str0: str = r"^CDLL\[\]$"

    # Execution
    str1: str = cdll0.__str__()

    # Validation
    assert match(str0, str1) is not None


def test___str___text_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    datas0: list[str] = [data0, data1, data2]
    cdll0: CDLL[str] = CDLL(values=datas0)
    str0: str = r"^CDLL\[" + f"'{data0}', '{data1}', '{data2}'" + r"\]$"

    # Execution
    str1: str = cdll0.__str__()

    # Validation
    assert match(str0, str1) is not None


def test___str___int_success():
    # Setup
    data0: int = 0
    data1: int = 1
    data2: int = 2
    datas0: list[int] = [data0, data1, data2]
    cdll0: CDLL[int] = CDLL(values=datas0)
    str0: str = r"^CDLL\[" + f"{data0}, {data1}, {data2}" + r"\]$"

    # Execution
    str1: str = cdll0.__str__()

    # Validation
    assert match(str0, str1) is not None


def test___str___float_success():
    # Setup
    data0: float = 0.1
    data1: float = 1.2
    data2: float = 2.3
    datas0: list[float] = [data0, data1, data2]
    cdll0: CDLL[float] = CDLL(values=datas0)
    str0: str = r"^CDLL\[" + f"{data0}, {data1}, {data2}" + r"\]$"

    # Execution
    str1: str = cdll0.__str__()

    # Validation
    assert match(str0, str1) is not None
