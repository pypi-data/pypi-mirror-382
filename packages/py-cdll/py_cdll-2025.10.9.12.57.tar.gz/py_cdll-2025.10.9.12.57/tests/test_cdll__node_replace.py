from src.py_cdll import CDLL
from src.py_cdll.node import Node, is_consistent, is_value_at_index


def test__node_replace_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "new_data"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data0, data3, data2]
    new_node: Node = Node(value=data3)
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._node_replace(target=cdll0._head.next, replacement=new_node)

    # Validation
    assert data1 not in cdll0
    assert cdll0._head.next is new_node
    assert cdll0._head.next.next.value == data2
    assert cdll0._head.next.previous.value == data0
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test__node_replace_reassign_head_on_overwrite_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "new_data"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data3, data1, data2]
    new_node: Node = Node(value=data3)
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._node_replace(target=cdll0._head, replacement=new_node)

    # Validation
    assert data0 not in cdll0
    assert cdll0._head is new_node
    assert cdll0._head.next.next.value == data2
    assert cdll0._head.previous.value == data2
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)
