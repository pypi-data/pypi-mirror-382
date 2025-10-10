from src.py_cdll.node import Node, nodes_from_values, length_step, is_consistent


def test_length_one_from_head_step_success():
    # Setup
    values0: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)
    amount0: int = 1

    # Execution
    amount1: int = length_step(node=node0)

    # Validation
    assert amount0 == amount1
    assert is_consistent(node=node0) is True


def test_length_two_from_head_step_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    node0: Node = nodes_from_values(values=values0)
    amount0: int = 2

    # Execution
    amount1: int = length_step(node=node0)

    # Validation
    assert amount0 == amount1
    assert is_consistent(node=node0) is True


def test_length_three_from_head_step_success():
    # Setup
    values0: list[str] = ["zero", "one", "two"]
    node0: Node = nodes_from_values(values=values0)
    amount0: int = 3

    # Execution
    amount1: int = length_step(node=node0)

    # Validation
    assert amount0 == amount1
    assert is_consistent(node=node0) is True


def test_length_four_from_last_step_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.previous
    amount0: int = 4

    # Execution
    amount1: int = length_step(node=node1)

    # Validation
    assert amount0 == amount1
    assert is_consistent(node=node0) is True


def test_length_five_from_middle_step_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four"]
    node0: Node = nodes_from_values(values=values0)
    node1: Node = node0.next.next
    amount0: int = 5

    # Execution
    amount1: int = length_step(node=node1)

    # Validation
    assert amount0 == amount1
    assert is_consistent(node=node0) is True
