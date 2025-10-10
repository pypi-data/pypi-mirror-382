from src.py_cdll.node import Node, remove, nodes_from_values, is_consistent, is_value_at_index


def test_remove_first_in_two_node_sequence_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    values1: list[str] = ["one"]
    values2: list[str] = ["zero"]
    head0: Node = nodes_from_values(values=values0)
    node0: Node = head0
    node1: Node = head0.next

    # Execution
    removed0: Node = remove(target=node0)

    # Validation
    assert removed0 is node0
    assert node0.next is node0
    assert node0.previous is node0
    assert node1.next is node1
    assert node1.previous is node1
    assert is_consistent(node=node0) is True
    assert is_consistent(node=node1) is True
    assert is_consistent(node=removed0) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=node1, reference=values1) is True
    assert is_value_at_index(node=removed0, reference=values2) is True


def test_remove_last_in_three_node_sequence_success():
    # Setup
    values0: list[str] = ["zero", "one", "two"]
    values1: list[str] = ["zero", "one"]
    values2: list[str] = ["two"]
    head0: Node = nodes_from_values(values=values0)
    node0: Node = head0
    node1: Node = head0.next
    node2: Node = head0.next.next

    # Execution
    removed0: Node = remove(target=node2)

    # Validation
    assert removed0 is node2
    assert node0.next is node1
    assert node0.previous is node1
    assert node1.next is node0
    assert node1.previous is node0
    assert node2.next is node2
    assert node2.previous is node2
    assert is_consistent(node=node0) is True
    assert is_consistent(node=node1) is True
    assert is_consistent(node=node2) is True
    assert is_consistent(node=removed0) is True
    assert is_value_at_index(node=head0, reference=values1) is True
    assert is_value_at_index(node=removed0, reference=values2) is True
    assert is_value_at_index(node=node1, reference=values1) is True
    assert is_value_at_index(node=node2, reference=values2) is True


def test_remove_middle_in_five_node_sequence_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four"]
    values1: list[str] = ["zero", "one", "three", "four"]
    values2: list[str] = ["two"]
    head0: Node = nodes_from_values(values=values0)
    node0: Node = head0
    node1: Node = head0.next
    node2: Node = head0.next.next
    node3: Node = head0.next.next.next
    node4: Node = head0.next.next.next.next

    # Execution
    removed0: Node = remove(target=node2)

    # Validation
    assert removed0 is node2
    assert node0.next is node1
    assert node0.previous is node4
    assert node1.next is node3
    assert node1.previous is node0
    assert node3.next is node4
    assert node3.previous is node1
    assert node4.next is node0
    assert node4.previous is node3
    assert node2.next is node2
    assert node2.previous is node2
    assert is_consistent(node=node0) is True
    assert is_consistent(node=node1) is True
    assert is_consistent(node=node2) is True
    assert is_consistent(node=node3) is True
    assert is_consistent(node=node4) is True
    assert is_consistent(node=removed0) is True
    assert is_value_at_index(node=head0, reference=values1) is True
    assert is_value_at_index(node=removed0, reference=values2) is True
    assert is_value_at_index(node=node1, reference=values1) is True
    assert is_value_at_index(node=node2, reference=values2) is True
