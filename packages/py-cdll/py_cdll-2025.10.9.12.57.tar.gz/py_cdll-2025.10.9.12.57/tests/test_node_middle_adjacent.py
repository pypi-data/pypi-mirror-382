from src.py_cdll.node import Node, middle_adjacent


def test_middle_adjacent_one_node_success():
    # Setup
    node0: Node = Node(value=None)
    node0.next = node0
    node0.previous = node0

    # Execution
    before_middle, after_middle = middle_adjacent(head=node0)

    # Validation
    assert before_middle is node0
    assert after_middle is node0


def test_middle_adjacent_two_nodes_success():
    # Setup
    node0: Node = Node(value=None)
    node1: Node = Node(value=None)
    node0.next = node1
    node1.previous = node0
    node1.next = node0
    node0.previous = node1

    # Execution
    before_middle, after_middle = middle_adjacent(head=node0)

    # Validation
    assert before_middle is node0
    assert after_middle is node1


def test_middle_adjacent_three_nodes_success():
    # Setup
    node0: Node = Node(value=None)
    node1: Node = Node(value=None)
    node2: Node = Node(value=None)
    node0.next = node1
    node1.previous = node0
    node1.next = node2
    node2.previous = node1
    node2.next = node0
    node0.previous = node2

    # Execution
    before_middle, after_middle = middle_adjacent(head=node0)

    # Validation
    assert before_middle is node1
    assert after_middle is node2


def test_middle_adjacent_four_nodes_success():
    # Setup
    node0: Node = Node(value=None)
    node1: Node = Node(value=None)
    node2: Node = Node(value=None)
    node3: Node = Node(value=None)
    node0.next = node1
    node1.previous = node0
    node1.next = node2
    node2.previous = node1
    node2.next = node3
    node3.previous = node2
    node3.next = node0
    node0.previous = node3

    # Execution
    before_middle, after_middle = middle_adjacent(head=node0)

    # Validation
    assert before_middle is node1
    assert after_middle is node2
