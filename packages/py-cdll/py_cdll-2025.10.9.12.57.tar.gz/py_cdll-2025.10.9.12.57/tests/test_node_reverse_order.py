from src.py_cdll.node import Node, reverse_order, is_consistent, nodes_from_values, is_value_at_index


def test_reverse_order_one_node_success():
    # Setup
    values0: list[str] = ["zero"]
    values1: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    reversed0: Node = reverse_order(head=node0)

    # Validation
    assert reversed0 is node0
    assert reversed0.head is node0
    assert reversed0.index == 0
    assert reversed0.next is node0
    assert reversed0.previous is node0
    assert is_consistent(node=reversed0) is True
    assert is_value_at_index(node=reversed0, reference=values1) is True


def test_reverse_order_two_node_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    values1: list[str] = ["one", "zero"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next

    # Execution
    reversed0: Node = reverse_order(head=node0)

    # Validation
    assert reversed0 is node1
    assert reversed0.head is node1
    assert reversed0.index == 0
    assert reversed0.next is node0
    assert reversed0.next.head is node1
    assert reversed0.next.index == 1
    assert reversed0.previous is node0
    assert is_consistent(node=reversed0) is True
    assert is_value_at_index(node=reversed0, reference=values1) is True


def test_reverse_order_five_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four"]
    values1: list[str] = ["four", "three", "two", "one", "zero"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next
    node2: Node = node0.next.next
    node3: Node = node0.next.next.next
    node4: Node = node0.next.next.next.next

    # Execution
    reversed0: Node = reverse_order(head=node0)

    # Validation
    assert reversed0 is node4
    assert reversed0.next is node3
    assert reversed0.next.next is node2
    assert reversed0.next.next.next is node1
    assert reversed0.next.next.next.next is node0
    assert reversed0.next.next.next.next.next is node4
    assert reversed0.previous is node0
    assert reversed0.previous.previous is node1
    assert reversed0.previous.previous.previous is node2
    assert reversed0.previous.previous.previous.previous is node3
    assert reversed0.previous.previous.previous.previous.previous is node4
    assert reversed0.index == 0
    assert reversed0.next.index == 1
    assert reversed0.next.next.index == 2
    assert reversed0.next.next.next.index == 3
    assert reversed0.next.next.next.next.index == 4
    assert reversed0.next.next.next.next.next.index == 0
    assert reversed0.head is node4
    assert reversed0.next.head is node4
    assert reversed0.next.next.head is node4
    assert reversed0.next.next.next.head is node4
    assert reversed0.next.next.next.next.head is node4
    assert reversed0.next.next.next.next.next.head is node4
    assert is_consistent(node=reversed0) is True
    assert is_value_at_index(node=reversed0, reference=values1) is True
