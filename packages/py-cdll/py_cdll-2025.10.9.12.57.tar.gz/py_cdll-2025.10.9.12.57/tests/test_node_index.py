from src.py_cdll.node import Node, insert_between, is_consistent


def test_index_one_node_success():
    # Setup
    node0: Node = Node(value="zero")

    # Validation
    assert node0.index == 0
    assert is_consistent(node=node0) is True


def test_index_two_nodes_insert_sequentially_success():
    # Setup
    node0: Node = Node(value="zero")
    node1: Node = Node(value="one")
    insert_between(before=node0, after=node0, insert=node1)

    # Validation
    assert node0.index == 0
    assert node1.index == 1
    assert is_consistent(node=node0) is True


def test_index_three_nodes_insert_sequentially_success():
    # Setup
    node0: Node = Node(value="zero")
    node1: Node = Node(value="one")
    node2: Node = Node(value="two")
    insert_between(before=node1, after=node1, insert=node2)
    insert_between(before=node0, after=node0, insert=node1)

    # Validation
    assert node0.index == 0
    assert node1.index == 1
    assert node2.index == 2
    assert is_consistent(node=node0) is True


def test_index_four_nodes_insert_sequentially_and_then_overwrite_head_success():
    # Setup
    node0: Node = Node(value="zero")
    node1: Node = Node(value="one")
    node2: Node = Node(value="two")
    node3: Node = Node(value="three")
    insert_between(before=node1, after=node1, insert=node2)
    insert_between(before=node0, after=node0, insert=node1)
    insert_between(before=node2, after=node0, insert=node3, head=node3)

    # Validation
    assert node0.index == 1
    assert node1.index == 2
    assert node2.index == 3
    assert node3.index == 0
    assert is_consistent(node=node0) is True
