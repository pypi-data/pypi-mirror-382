from src.py_cdll.node import Node, nodes_from_values, is_value_at_index


def test_is_value_at_index_one_value_success():
    # Setup
    values0: list[str] = ["zero"]
    values1: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is True


def test_is_value_at_index_four_values_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three"]
    values1: list[str] = ["zero", "one", "two", "three"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is True


def test_is_value_at_index_seven_values_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six"]
    values1: list[str] = ["zero", "one", "two", "three", "four", "five", "six"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is True


def test_is_value_at_index_five_values_one_incorrect_value_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four"]
    values1: list[str] = ["zero", "one", "two", "incorrect", "four"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is False


def test_is_value_at_index_five_values_two_indices_mixed_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four"]
    values1: list[str] = ["zero", "one", "three", "two", "four"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is False


def test_is_value_at_index_five_values_three_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one", "two"]
    values1: list[str] = ["zero", "one", "two", "three", "four"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is False


def test_is_value_at_index_three_values_five_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four"]
    values1: list[str] = ["zero", "one", "two"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    bool0: bool = is_value_at_index(node=node0, reference=values1)

    # Validation
    assert bool0 is False
