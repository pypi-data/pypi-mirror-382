from collections.abc import Iterator

import pytest

from src.py_cdll.node import Node, nodes_from_values, nodes, remove, insert_between, is_consistent


def test_nodes_five_items_success():
    # Setup
    head0: Node = nodes_from_values(values=[0, 1, 2, 3, 4])
    iterator0: Iterator[Node] = nodes(head=head0)

    # Execution
    node0: Node = next(iterator0)
    node1: Node = next(iterator0)
    node2: Node = next(iterator0)
    node3: Node = next(iterator0)
    node4: Node = next(iterator0)

    # Validation
    assert head0 is node0
    assert head0.next is node1
    assert head0.next.next is node2
    assert head0.next.next.next is node3
    assert head0.next.next.next.next is node4
    assert head0.previous is node4
    assert head0.previous.previous is node3
    assert head0.previous.previous.previous is node2
    assert head0.previous.previous.previous.previous is node1
    assert head0.previous.previous.previous.previous.previous is node0
    assert is_consistent(node=head0)


def test_nodes_five_items_middle_removed_success():
    # Setup
    head0: Node = nodes_from_values(values=[0, 1, 2, 3, 4])
    node2: Node = head0.next.next
    iterator0: Iterator[Node] = nodes(head=head0)

    # Execution
    remove(target=node2)
    node0: Node = next(iterator0)
    node1: Node = next(iterator0)
    node3: Node = next(iterator0)
    node4: Node = next(iterator0)

    # Validation
    with pytest.raises(StopIteration):
        _ = next(iterator0)

    assert head0 is node0
    assert head0.next is node1
    assert head0.next.next is node3
    assert head0.next.next.next is node4
    assert head0.previous is node4
    assert head0.previous.previous is node3
    assert head0.previous.previous.previous is node1
    assert head0.previous.previous.previous.previous is node0
    assert is_consistent(node=head0)


def test_nodes_five_items_three_steps_remove_three_failure():
    # Setup
    head0: Node = nodes_from_values(values=[0, 1, 2, 3, 4])
    node2: Node = head0.next.next
    node3: Node = head0.next.next.next
    node4: Node = head0.next.next.next.next
    iterator0: Iterator[Node] = nodes(head=head0)

    # Execution
    node0: Node = next(iterator0)
    node1: Node = next(iterator0)
    _: Node = next(iterator0)
    _: Node = remove(target=node2)
    _: Node = remove(target=node3)
    _: Node = remove(target=node4)

    # Validation
    with pytest.raises(StopIteration):
        _ = next(iterator0)

    assert head0 is node0
    assert head0.next is node1
    assert head0.previous is node1
    assert head0.previous.previous is node0
    assert is_consistent(node=head0)


def test_nodes_five_items_three_steps_pop_four_append_five_success():
    # Setup
    head0: Node = nodes_from_values(values=[0, 1, 2, 3, 4])
    head1: Node = nodes_from_values(values=[5, 6, 7, 8, 9])
    node3: Node = head0.next.next.next
    node4: Node = head0.next.next.next.next
    iterator0: Iterator[Node] = nodes(head=head0)

    # Execution
    node0: Node = next(iterator0)
    node1: Node = next(iterator0)
    node2: Node = next(iterator0)
    _: Node = remove(target=node1)
    _: Node = remove(target=node2)
    _: Node = remove(target=node3)
    _: Node = remove(target=node4)
    insert_between(before=node0, after=node0, insert=head1)
    node3: Node = next(iterator0)
    node4: Node = next(iterator0)
    node5: Node = next(iterator0)

    # Validation
    with pytest.raises(StopIteration):
        _ = next(iterator0)

    assert head0 is node0
    assert head0.next is head1
    assert head0.next.next is head1.next
    assert head0.next.next.next is node3
    assert head0.next.next.next.next is node4
    assert head0.next.next.next.next.next is node5
    assert head0.previous is node5
    assert head0.previous.previous is node4
    assert head0.previous.previous.previous is node3
    assert head0.previous.previous.previous.previous is head1.next
    assert head0.previous.previous.previous.previous.previous is head1
    assert is_consistent(node=head0)
    assert is_consistent(node=head1)


def test_nodes_with_callback_five_items_three_steps_pop_four_append_five_success():
    # Setup
    head0: Node = nodes_from_values(values=[0, 1, 2, 3, 4])
    head1: Node = nodes_from_values(values=[5, 6, 7, 8, 9])
    node3: Node = head0.next.next.next
    node4: Node = head0.next.next.next.next
    callback0: Node = head0
    iterator0: Iterator[Node] = nodes(head=head0, callback=lambda: callback0)

    # Execution
    node0: Node = next(iterator0)
    node1: Node = next(iterator0)
    node2: Node = next(iterator0)
    _: Node = remove(target=node1)
    _: Node = remove(target=node2)
    _: Node = remove(target=node3)
    _: Node = remove(target=node4)
    insert_between(before=node0, after=node0, insert=head1, head=head1)
    callback0: Node = head1
    node3: Node = next(iterator0)
    node4: Node = next(iterator0)
    node5: Node = next(iterator0)

    # Validation
    with pytest.raises(StopIteration):
        _ = next(iterator0)

    assert head0 is node0
    assert head0.next is head1
    assert head0.next.next is head1.next
    assert head0.next.next.next is head1.next.next
    assert head0.next.next.next.next is node3
    assert head0.next.next.next.next.next is node4
    assert head0.next.next.next.next.next.next is node5
    assert head0.previous is node4
    assert head0.previous.previous is node3
    assert head0.previous.previous.previous is head1.next.next
    assert head0.previous.previous.previous.previous is head1.next
    assert head0.previous.previous.previous.previous.previous is head1
    assert is_consistent(node=head0)
    assert is_consistent(node=head1)
