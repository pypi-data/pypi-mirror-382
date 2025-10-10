from src.py_cdll.node import Node, is_consistent


########################################################################################################################


def test_node_with_data_success():
    data: str = "data"
    node: Node = Node(data)

    # Validation
    assert node.value == data
    assert is_consistent(node=node) is True


########################################################################################################################
