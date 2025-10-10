import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import Node, merge, is_consistent, is_value_at_index


def test_merge_first_wrong_type_second_one_failure():
    # Setup
    first: str = "wrong type"
    datas1: list[int] = [0]
    cdll1: CDLL = CDLL(values=datas1)
    second: Node = cdll1._head

    # Validation
    with pytest.raises(AttributeError):
        # noinspection PyTypeChecker
        merge(first=first, second=second)


def test_merge_first_one_second_wrong_type_failure():
    # Setup
    datas0: list[int] = [0]
    cdll0: CDLL = CDLL(values=datas0)
    first: Node = cdll0._head
    second: str = "wrong type"

    # Validation
    with pytest.raises(AttributeError):
        # noinspection PyTypeChecker
        merge(first=first, second=second)


def test_merge_first_zero_second_zero_success():
    # Setup
    values0: list[int] = [0]
    values1: list[int] = [0]
    values2: list[int] = [0, 0]
    cdll0: CDLL = CDLL(values=values0)
    first: Node = cdll0._head
    cdll1: CDLL = CDLL(values=values1)
    second: Node = cdll1._head

    # Execution
    merged: Node = merge(first=first, second=second)

    # Validation
    assert merged is first
    assert merged.next is second
    assert merged.next.next is first
    assert merged.next.previous is first
    assert merged.previous is second
    assert merged.previous.next is first
    assert merged.previous.previous is first
    assert is_consistent(node=cdll0._head) is True
    assert is_consistent(node=cdll1._head) is True
    assert is_consistent(node=merged) is True
    assert is_value_at_index(node=first, reference=values2) is True
    assert is_value_at_index(node=second, reference=values2) is True


def test_merge_first_zero_second_one_success():
    # Setup
    values0: list[int] = [0]
    values1: list[int] = [1]
    values2: list[int] = [0, 1]
    cdll0: CDLL = CDLL(values=values0)
    first: Node = cdll0._head
    cdll1: CDLL = CDLL(values=values1)
    second: Node = cdll1._head

    # Execution
    merged: Node = merge(first=first, second=second)

    # Validation
    assert merged is first
    assert merged.next is second
    assert merged.next.next is first
    assert merged.next.previous is first
    assert merged.previous is second
    assert merged.previous.next is first
    assert merged.previous.previous is first
    assert is_consistent(node=cdll0._head) is True
    assert is_consistent(node=cdll1._head) is True
    assert is_consistent(node=merged) is True
    assert is_value_at_index(node=first, reference=values2) is True
    assert is_value_at_index(node=second, reference=values2) is True


def test_merge_first_one_second_zero_success():
    # Setup
    values0: list[int] = [1]
    values1: list[int] = [0]
    values2: list[int] = [0, 1]
    cdll0: CDLL = CDLL(values=values0)
    first: Node = cdll0._head
    cdll1: CDLL = CDLL(values=values1)
    second: Node = cdll1._head

    # Execution
    merged: Node = merge(first=first, second=second)

    # Validation
    assert merged is second
    assert merged.next is first
    assert merged.next.next is second
    assert merged.next.previous is second
    assert merged.previous is first
    assert merged.previous.next is second
    assert merged.previous.previous is second
    assert is_consistent(node=cdll0._head) is True
    assert is_consistent(node=cdll1._head) is True
    assert is_consistent(node=merged) is True
    assert is_value_at_index(node=first, reference=values2) is True
    assert is_value_at_index(node=second, reference=values2) is True


def test_merge_first_zero_and_two_second_one_success():
    # Setup
    values0: list[int] = [0, 2]
    values1: list[int] = [1]
    values2: list[int] = [0, 1, 2]
    cdll0: CDLL = CDLL(values=values0)
    first0: Node = cdll0._head
    first1: Node = first0.next
    cdll1: CDLL = CDLL(values=values1)
    second0: Node = cdll1._head

    # Execution
    merged: Node = merge(first=first0, second=second0)

    # Validation
    assert merged is first0
    assert merged.next is second0
    assert merged.previous is first1

    assert merged.next.next is first1
    assert merged.next.previous is first0

    assert merged.next.next.next is first0
    assert merged.next.next.previous is second0

    assert merged.previous.next is first0
    assert merged.previous.previous is second0

    assert is_consistent(node=cdll0._head) is True
    assert is_consistent(node=cdll1._head) is True
    assert is_consistent(node=merged) is True
    assert is_value_at_index(node=first0, reference=values2) is True
    assert is_value_at_index(node=first1, reference=values2) is True
    assert is_value_at_index(node=second0, reference=values2) is True


def test_merge_first_five_second_two_and_seven_success():
    # Setup
    values0: list[int] = [5]
    values1: list[int] = [2, 7]
    values2: list[int] = [2, 5, 7]
    cdll0: CDLL = CDLL(values=values0)
    first0: Node = cdll0._head
    cdll1: CDLL = CDLL(values=values1)
    second0: Node = cdll1._head
    second1: Node = second0.next

    # Execution
    merged: Node = merge(first=first0, second=second0)

    # Validation
    assert merged is second0
    assert merged.next is first0
    assert merged.previous is second1

    assert merged.next.next is second1
    assert merged.next.previous is second0

    assert merged.next.next.next is second0
    assert merged.next.next.previous is first0

    assert merged.previous.next is second0
    assert merged.previous.previous is first0

    assert is_consistent(node=cdll0._head) is True
    assert is_consistent(node=cdll1._head) is True
    assert is_consistent(node=merged) is True
    assert is_value_at_index(node=first0, reference=values2) is True
    assert is_value_at_index(node=second0, reference=values2) is True
    assert is_value_at_index(node=second1, reference=values2) is True


def test_merge_first_seven_and_thirteen_second_three_and_sixteen_success():
    # Setup
    values0: list[int] = [7, 13]
    values1: list[int] = [3, 16]
    values2: list[int] = [3, 7, 13, 16]
    cdll0: CDLL = CDLL(values=values0)
    first0: Node = cdll0._head
    first1: Node = first0.next
    cdll1: CDLL = CDLL(values=values1)
    second0: Node = cdll1._head
    second1: Node = second0.next

    # Execution
    merged: Node = merge(first=first0, second=second0)

    # Validation
    assert merged is second0
    assert merged.next is first0
    assert merged.previous is second1

    assert merged.next.next is first1
    assert merged.next.previous is second0

    assert merged.next.next.next is second1
    assert merged.next.next.previous is first0

    assert merged.next.next.next.next is second0
    assert merged.next.next.next.previous is first1

    assert merged.previous.next is second0
    assert merged.previous.previous is first1

    assert is_consistent(node=cdll0._head) is True
    assert is_consistent(node=cdll1._head) is True
    assert is_consistent(node=merged) is True
    assert is_value_at_index(node=first0, reference=values2) is True
    assert is_value_at_index(node=second0, reference=values2) is True
    assert is_value_at_index(node=second1, reference=values2) is True
