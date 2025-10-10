from src.py_cdll.node import Node, split_head_from_tail, nodes_from_values, is_consistent, is_value_at_index


def test_split_head_from_tail_one_node_success():
    # Setup
    values0: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    head0, tail0 = split_head_from_tail(node=node0)

    # Validation
    assert head0 is node0
    assert head0.next is node0
    assert head0.previous is node0
    assert tail0 is None
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values0) is True


def test_split_head_from_tail_two_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    values1: list[str] = ["zero"]
    values2: list[str] = ["one"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next

    # Execution
    head0, tail0 = split_head_from_tail(node=node0)

    # Validation
    assert head0 is node0
    assert head0.next is node0
    assert head0.previous is node0
    assert tail0 is node1
    assert tail0.next is node1
    assert tail0.previous is node1
    assert is_consistent(node=head0) is True
    assert is_consistent(node=tail0) is True
    assert is_value_at_index(node=head0, reference=values1) is True
    assert is_value_at_index(node=tail0, reference=values2) is True


def test_split_head_from_tail_three_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one", "two"]
    values1: list[str] = ["zero"]
    values2: list[str] = ["one", "two"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next
    node2: Node = node0.next.next

    # Execution
    head0, tail0 = split_head_from_tail(node=node0)

    # Validation
    assert head0 is node0
    assert head0.next is head0
    assert head0.previous is head0
    assert tail0 is node1
    assert tail0.next is node2
    assert tail0.previous is node2
    assert is_consistent(node=head0) is True
    assert is_consistent(node=tail0) is True
    assert is_value_at_index(node=head0, reference=values1) is True
    assert is_value_at_index(node=tail0, reference=values2) is True


def test_split_head_from_tail_four_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three"]
    values1: list[str] = ["zero"]
    values2: list[str] = ["one", "two", "three"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next
    node2: Node = node0.next.next
    node3: Node = node0.next.next.next

    # Execution
    head0, tail0 = split_head_from_tail(node=node0)

    # Validation
    assert head0 is node0
    assert head0.next is head0
    assert head0.previous is head0
    assert tail0 is node1
    assert tail0.next is node2
    assert tail0.previous is node3
    assert is_consistent(node=head0) is True
    assert is_consistent(node=tail0) is True
    assert is_value_at_index(node=head0, reference=values1) is True
    assert is_value_at_index(node=tail0, reference=values2) is True
