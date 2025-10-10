import pytest

from src.py_cdll import CDLL
from src.py_cdll.node import split_in_middle, Node, is_consistent, is_value_at_index


def test_split_in_middle_wrong_type_failure():
    # Setup
    node: str = "not a node"

    # Validation
    with pytest.raises(AttributeError):
        # noinspection PyTypeChecker
        split_in_middle(head=node)


def test_split_in_middle_cdll_one_node_success():
    # Setup
    values0: list[int] = [0]
    cdll0: CDLL = CDLL(values=values0)
    head0: Node = cdll0._head

    # Execution
    new_head, new_middle = split_in_middle(head=head0)

    # Validation
    assert new_head is head0
    assert new_head.next is head0
    assert new_head.previous is head0
    assert new_middle is head0
    assert new_middle.next is head0
    assert new_middle.previous is head0
    assert is_consistent(node=new_head) is True
    assert is_consistent(node=new_middle) is True
    assert is_value_at_index(node=new_head, reference=values0) is True
    assert is_value_at_index(node=new_middle, reference=values0) is True


def test_split_in_middle_cdll_two_nodes_success():
    # Setup
    values0: list[int] = [0, 1]
    values1: list[int] = [0]
    values2: list[int] = [1]
    cdll0: CDLL = CDLL(values=values0)
    head0: Node = cdll0._head
    last0: Node = head0.next

    # Execution
    new_head, new_middle = split_in_middle(head=head0)

    # Validation
    assert new_head is head0
    assert new_head.next is head0
    assert new_head.previous is head0
    assert new_middle is last0
    assert new_middle.next is last0
    assert new_middle.previous is last0
    assert is_consistent(node=new_head) is True
    assert is_consistent(node=new_middle) is True
    assert is_value_at_index(node=new_head, reference=values1) is True
    assert is_value_at_index(node=new_middle, reference=values2) is True


def test_split_in_middle_cdll_three_nodes_success():
    # Setup
    values0: list[int] = [0, 1, 2]
    values1: list[int] = [0, 1]
    values2: list[int] = [2]
    cdll0: CDLL = CDLL(values=values0)
    head0: Node = cdll0._head
    middle0: Node = head0.next
    last0: Node = head0.previous

    # Execution
    new_head, new_middle = split_in_middle(head=head0)

    # Validation
    assert new_head is head0
    assert new_head.next is middle0
    assert new_head.previous is middle0
    assert new_middle is last0
    assert new_middle.next is last0
    assert new_middle.previous is last0
    assert is_consistent(node=new_head) is True
    assert is_consistent(node=new_middle) is True
    assert is_value_at_index(node=new_head, reference=values1) is True
    assert is_value_at_index(node=new_middle, reference=values2) is True


def test_split_in_middle_cdll_four_nodes_success():
    # Setup
    values0: list[int] = [0, 1, 2, 3]
    values1: list[int] = [0, 1]
    values2: list[int] = [2, 3]
    cdll0: CDLL = CDLL(values=values0)
    head0: Node = cdll0._head
    second0: Node = head0.next
    third0: Node = second0.next
    last0: Node = third0.next

    # Execution
    new_head, new_middle = split_in_middle(head=head0)

    # Validation
    assert new_head is head0
    assert new_head.next is second0
    assert new_head.previous is second0
    assert new_middle is third0
    assert new_middle.next is last0
    assert new_middle.previous is last0
    assert is_consistent(node=new_head) is True
    assert is_consistent(node=new_middle) is True
    assert is_value_at_index(node=new_head, reference=values1) is True
    assert is_value_at_index(node=new_middle, reference=values2) is True


def test_split_in_middle_cdll_seven_nodes_success():
    # Setup
    values0: list[int] = [0, 1, 2, 3, 4, 5, 6]
    values1: list[int] = [0, 1, 2, 3]
    values2: list[int] = [4, 5, 6]
    cdll0: CDLL = CDLL(values=values0)
    head0: Node = cdll0._head
    second0: Node = head0.next
    third0: Node = second0.next
    fourth0: Node = third0.next
    fifth0: Node = fourth0.next
    sixth0: Node = fifth0.next
    last0: Node = sixth0.next

    # Execution
    new_head, new_middle = split_in_middle(head=head0)

    # Validation
    assert new_head is head0
    assert new_head.next is second0
    assert new_head.previous is fourth0
    assert new_middle is fifth0
    assert new_middle.next is sixth0
    assert new_middle.previous is last0
    assert is_consistent(node=new_head) is True
    assert is_consistent(node=new_middle) is True
    assert is_value_at_index(node=new_head, reference=values1) is True
    assert is_value_at_index(node=new_middle, reference=values2) is True
