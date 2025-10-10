from src.py_cdll import CDLL


def test___eq___other_type_success():
    # Setup
    cdll0: CDLL = CDLL()
    other0: float = 3.14

    # Execution
    # noinspection PyTypeChecker
    equal: bool = cdll0 == other0

    # Validation
    assert equal is False


def test___eq___empty_and_empty_success():
    # Setup
    cdll0: CDLL = CDLL()
    cdll1: CDLL = CDLL()

    # Execution
    equal: bool = cdll0 == cdll1

    # Validation
    assert equal is True


def test___eq___one_and_one_success():
    # Setup
    data0: int = 0
    data1: int = 0
    datas0: list[int] = [data0]
    datas1: list[int] = [data1]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)

    # Execution
    equal: bool = cdll0 == cdll1

    # Validation
    assert equal is True


def test___eq___six_and_six_success():
    # Setup
    data00: int = 0
    data01: int = 1
    data02: int = 2
    data03: int = 3
    data04: int = 4
    data05: int = 5
    data10: int = 0
    data11: int = 1
    data12: int = 2
    data13: int = 3
    data14: int = 4
    data15: int = 5
    datas0: list[int] = [data00, data01, data02, data03, data04, data05]
    datas1: list[int] = [data10, data11, data12, data13, data14, data15]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)

    # Execution
    equal: bool = cdll0 == cdll1

    # Validation
    assert equal is True


def test___eq___one_and_zero_success():
    # Setup
    data0: int = 0
    datas0: list[int] = [data0]
    datas1: list[int] = []
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)

    # Execution
    equal: bool = cdll0 == cdll1

    # Validation
    assert equal is False


def test___eq___zero_and_one_success():
    # Setup
    data0: int = 0
    datas0: list[int] = []
    datas1: list[int] = [data0]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)

    # Execution
    equal: bool = cdll0 == cdll1

    # Validation
    assert equal is False


def test___eq___four_and_four_last_different_success():
    # Setup
    data00: int = 0
    data01: int = 1
    data02: int = 2
    data03: int = 3
    data10: int = 0
    data11: int = 1
    data12: int = 2
    data13: int = 33
    datas0: list[int] = [data00, data01, data02, data03]
    datas1: list[int] = [data10, data11, data12, data13]
    cdll0: CDLL = CDLL(values=datas0)
    cdll1: CDLL = CDLL(values=datas1)

    # Execution
    equal: bool = cdll0 == cdll1

    # Validation
    assert equal is False
