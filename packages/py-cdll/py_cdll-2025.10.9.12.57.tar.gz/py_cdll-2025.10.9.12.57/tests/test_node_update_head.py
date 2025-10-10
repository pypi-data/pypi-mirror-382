from src.py_cdll.node import Node, nodes_from_values, equal, update_head, is_consistent, is_value_at_index


def test_update_head_one_item_first_success():
    # Setup
    values0: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values0)
    node2: Node = node0.next

    # Execution
    update_head(node=node2)

    # Validation
    assert equal(first=node2, second=node1)
    assert is_consistent(node=node2) is True
    assert is_value_at_index(node=node0, reference=values0) is True
    assert is_value_at_index(node=node2, reference=values0) is True


def test_update_head_two_item_second_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    values1: list[str] = ["one", "zero"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values1)
    node2: Node = node0.next

    # Execution
    update_head(node=node2)

    # Validation
    assert equal(first=node2, second=node1)
    assert is_consistent(node=node2) is True
    assert is_value_at_index(node=node0, reference=values1) is True
    assert is_value_at_index(node=node2, reference=values1) is True


def test_update_head_three_item_second_success():
    # Setup
    values0: list[str] = ["zero", "one", "two"]
    values1: list[str] = ["one", "two", "zero"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values1)
    node2: Node = node0.next

    # Execution
    update_head(node=node2)

    # Validation
    assert equal(first=node2, second=node1)
    assert is_consistent(node=node2) is True
    assert is_value_at_index(node=node0, reference=values1) is True
    assert is_value_at_index(node=node2, reference=values1) is True


def test_update_head_four_item_third_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three"]
    values1: list[str] = ["two", "three", "zero", "one"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = nodes_from_values(values=values1)
    node2: Node = node0.next.next

    # Execution
    update_head(node=node2)

    # Validation
    assert equal(first=node2, second=node1)
    assert is_consistent(node=node2) is True
    assert is_value_at_index(node=node0, reference=values1) is True
    assert is_value_at_index(node=node2, reference=values1) is True
