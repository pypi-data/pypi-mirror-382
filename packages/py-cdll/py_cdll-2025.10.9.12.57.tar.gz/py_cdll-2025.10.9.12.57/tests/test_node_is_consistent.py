from src.py_cdll.node import nodes_from_values, Node, is_consistent


def test_is_consistent_one_node_success():
    # Setup
    values0: list[str] = ["zero"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    is_alright: bool = is_consistent(node=node0)

    # Validation
    assert is_alright is True


def test_is_consistent_two_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    is_alright: bool = is_consistent(node=node0)

    # Validation
    assert is_alright is True


def test_is_consistent_seven_nodes_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six"]
    node0: Node = nodes_from_values(values=values0)

    # Execution
    is_alright: bool = is_consistent(node=node0)

    # Validation
    assert is_alright is True


def test_is_consistent_eight_nodes_wrong_head_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six", "seven"]
    node0: Node = nodes_from_values(values=values0)
    is_alright0: bool = is_consistent(node=node0)

    # Verification
    assert is_alright0 is True

    # Execution
    node1: Node = Node(value=None)
    node0.next.next.next.next.next.head = node1
    is_alright1: bool = is_consistent(node=node0)

    # Validation
    assert is_alright1 is False


def test_is_consistent_nine_nodes_wrong_index_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]
    node0: Node = nodes_from_values(values=values0)
    is_alright0: bool = is_consistent(node=node0)

    # Verification
    assert is_alright0 is True

    # Execution
    index0: int = 999999
    node0.next.next.next.next.next.next.index = index0
    is_alright1: bool = is_consistent(node=node0)

    # Validation
    assert is_alright1 is False


def test_is_consistent_ten_nodes_wrong_previous_success():
    # Setup
    values0: list[str] = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    node0: Node = nodes_from_values(values=values0)
    is_alright0: bool = is_consistent(node=node0)

    # Verification
    assert is_alright0 is True

    # Execution
    node1: Node = Node(value=None)
    node0.next.next.next.next.next.next.next.previous = node1
    is_alright1: bool = is_consistent(node=node0)

    # Validation
    assert is_alright1 is False
