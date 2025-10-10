from src.py_cdll import CDLL
from src.py_cdll.node import Node, before_target, is_consistent


def test_before_first_zero_second_one_success():
    # Setup
    first: Node = CDLL(values=[0])._head
    second: Node = CDLL(values=[1])._head
    current: Node = first
    before_insert0: Node = first

    # Execution
    before_insert1: Node = before_target(current=current, head=first, target=second)

    # Validation
    assert before_insert0 == before_insert1
    assert is_consistent(node=before_insert1) is True


def test_before_first_one_second_one_success():
    # Setup
    first: Node = CDLL(values=[1])._head
    second: Node = CDLL(values=[1])._head
    current: Node = first
    before_insert0: Node = first

    # Execution
    before_insert1: Node = before_target(current=current, head=first, target=second)

    # Validation
    assert before_insert0 == before_insert1
    assert is_consistent(node=before_insert1) is True


def test_before_first_one_three_second_six_success():
    # Setup
    first: Node = CDLL(values=[1, 3])._head
    second: Node = CDLL(values=[6])._head
    current: Node = first
    before_insert0: Node = first.next

    # Execution
    before_insert1: Node = before_target(current=current, head=first, target=second)

    # Validation
    assert before_insert0 == before_insert1
    assert is_consistent(node=before_insert1) is True


def test_before_first_two_seven_second_four_six_success():
    # Setup
    first: Node = CDLL(values=[2, 7])._head
    second: Node = CDLL(values=[4, 6])._head
    current: Node = first
    before_insert0: Node = first

    # Execution
    before_insert1: Node = before_target(current=current, head=first, target=second)

    # Validation
    assert before_insert0 == before_insert1
    assert is_consistent(node=before_insert1) is True
