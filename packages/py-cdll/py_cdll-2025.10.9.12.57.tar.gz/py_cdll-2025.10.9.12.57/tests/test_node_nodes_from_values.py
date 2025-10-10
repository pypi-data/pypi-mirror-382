from src.py_cdll.node import Node, nodes_from_values, is_consistent, is_value_at_index


def test_nodes_from_values_empty_failure():
    # Setup
    datas0: list[str] = []
    values0: None = None

    # Execution
    values1: None = nodes_from_values(values=datas0)

    # Validation
    assert values1 == values0


def test_nodes_from_values_one_value_success():
    # Setup
    data0: str = "data0"
    values0: list[str] = [data0]

    # Execution
    head0: Node = nodes_from_values(values=values0)

    # Validation
    assert head0.value is data0
    assert head0.next is head0
    assert head0.previous is head0
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values0) is True


def test_nodes_from_values_two_values_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    values0: list[str] = [data0, data1]

    # Execution
    head0: Node = nodes_from_values(values=values0)

    # Validation
    assert head0.value is data0
    assert head0.next.value is data1
    assert head0.previous.value is data1
    assert head0.next.next is head0
    assert head0.previous.previous is head0
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values0) is True


def test_nodes_from_values_seven_values_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    values0: list[str] = [data0, data1, data2, data3, data4, data5, data6]

    # Execution
    head0: Node = nodes_from_values(values=values0)

    # Validation
    assert head0.value is data0
    assert head0.next.value is data1
    assert head0.next.next.value is data2
    assert head0.next.next.next.value is data3
    assert head0.next.next.next.next.value is data4
    assert head0.next.next.next.next.next.value is data5
    assert head0.next.next.next.next.next.next.value is data6
    assert head0.next.next.next.next.next.next.next.value is data0
    assert head0.previous.value is data6
    assert head0.previous.previous.value is data5
    assert head0.previous.previous.previous.value is data4
    assert head0.previous.previous.previous.previous.value is data3
    assert head0.previous.previous.previous.previous.previous.value is data2
    assert head0.previous.previous.previous.previous.previous.previous.value is data1
    assert head0.previous.previous.previous.previous.previous.previous.previous.value is data0
    assert head0.next.next.next.next.next.next.next is head0
    assert head0.previous.previous.previous.previous.previous.previous.previous is head0
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values0) is True
