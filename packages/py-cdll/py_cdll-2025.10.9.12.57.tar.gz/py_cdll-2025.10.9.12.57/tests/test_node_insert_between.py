import pytest

from src.py_cdll import NoNewHeadError
from src.py_cdll.node import Node, insert_between, nodes_from_values, equal, is_consistent, is_value_at_index, length


def test_insert_between_first_zero_second_one_success():
    # Setup
    values0: list[int] = [0]
    values1: list[int] = [1]
    values2: list[int] = [0, 1]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0
    after0: Node = head0.next
    insert0: Node = head1
    removed0: None = None

    # Execution
    removed1: None = insert_between(before=before0, after=after0, insert=insert0)

    # Validation
    assert removed1 is removed0
    assert equal(first=head0, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_seven_second_none_success():
    # Setup
    values0: list[int] = [7]
    head0: Node = nodes_from_values(values=values0)
    head1: None = None
    head2: Node = nodes_from_values(values=values0)
    before0: Node = head0
    after0: Node = head0.next
    insert0: None = head1

    # Execution
    inserted0: None = insert_between(before=before0, after=after0, insert=insert0)

    # Validation
    assert inserted0 is insert0
    assert equal(first=head0, second=head2)
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values0) is True
    assert is_value_at_index(node=head2, reference=values0) is True


def test_insert_between_first_zero_two_second_one_success():
    # Setup
    values0: list[int] = [0, 2]
    values1: list[int] = [1]
    values2: list[int] = [0, 1, 2]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0
    after0: Node = head0.next
    insert0: Node = head1
    removed0: None = None

    # Execution
    removed1: None = insert_between(before=before0, after=after0, insert=insert0)

    # Validation
    assert removed1 is removed0
    assert equal(first=head0, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_five_seven_second_three_replace_head_success():
    # Setup
    values0: list[int] = [5, 7]
    values1: list[int] = [3]
    values2: list[int] = [3, 7]
    values3: list[int] = [5]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0.previous
    after0: Node = head0.next
    insert0: Node = head1
    removed0: Node = head0

    # Execution
    removed1: Node = insert_between(before=before0, after=after0, insert=insert0, head=head1)

    # Validation
    assert removed1 is removed0
    assert equal(first=head1, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_value_at_index(node=head0, reference=values3) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_five_seven_nine_second_three_replace_head_success():
    # Setup
    values0: list[int] = [5, 7, 9]
    values1: list[int] = [3]
    values2: list[int] = [3, 7, 9]
    values3: list[int] = [5]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0.previous
    after0: Node = head0.next
    insert0: Node = head1
    removed0: Node = head0

    # Execution
    removed1: Node = insert_between(before=before0, after=after0, insert=insert0, head=head1)

    # Validation
    assert removed1 is removed0
    assert length(node=head0) == 1
    assert equal(first=head1, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_consistent(node=removed1) is True
    assert is_value_at_index(node=head0, reference=values3) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_five_seven_nine_ten_second_three_replace_head_success():
    # Setup
    values0: list[int] = [5, 7, 9, 10]
    values1: list[int] = [3]
    values2: list[int] = [3, 7, 9, 10]
    values3: list[int] = [5]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0.previous
    after0: Node = head0.next
    insert0: Node = head1
    removed0: Node = head0

    # Execution
    removed1: Node = insert_between(before=before0, after=after0, insert=insert0, head=head1)

    # Validation
    assert removed1 is removed0
    assert length(node=head0) == 1
    assert equal(first=head1, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_consistent(node=removed1) is True
    assert is_value_at_index(node=head0, reference=values3) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_three_nine_second_none_success():
    # Setup
    values0: list[int] = [3, 9]
    head0: Node = nodes_from_values(values=values0)
    head1: None = None
    head2: Node = nodes_from_values(values=values0)
    before0: Node = head0
    after0: Node = head0.next
    insert0: None = head1

    # Execution
    inserted0: None = insert_between(before=before0, after=after0, insert=insert0)

    # Validation
    assert inserted0 is insert0
    assert equal(first=head0, second=head2)
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values0) is True
    assert is_value_at_index(node=head2, reference=values0) is True


def test_insert_between_first_three_nine_second_none_remove_success():
    # Setup
    values0: list[int] = [3, 9]
    values1: list[int] = [9]
    values2: list[int] = [3]
    head0: Node = nodes_from_values(values=values0)
    head1: None = None
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0
    after0: Node = head0
    insert0: None = head1
    removed0: Node = head0.next

    # Execution
    removed1: Node = insert_between(before=before0, after=after0, insert=insert0)

    # Validation
    assert removed1 is removed0
    assert equal(first=removed1, second=removed0)
    assert equal(first=head0, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=removed1) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True
    assert is_value_at_index(node=removed1, reference=values1) is True


def test_insert_between_first_five_twelve_second_two_success():
    # Setup
    values0: list[int] = [5, 12]
    values1: list[int] = [2]
    values2: list[int] = [2, 5, 12]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0.previous
    after0: Node = head0
    insert0: Node = head1
    removed0: None = None

    # Execution
    removed1: None = insert_between(before=before0, after=after0, insert=insert0, head=insert0)

    # Validation
    assert removed1 is removed0
    assert equal(first=head1, second=head2)
    assert is_consistent(node=head0) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_five_twelve_second_two_four_success():
    # Setup
    values0: list[int] = [5, 12]
    values1: list[int] = [2, 4]
    values2: list[int] = [2, 4, 5, 12]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0.previous
    after0: Node = head0
    insert0: Node = head1
    removed0: None = None

    # Execution
    removed1: None = insert_between(before=before0, after=after0, insert=insert0, head=insert0)

    # Validation
    assert removed1 is removed0
    assert equal(first=head1, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True


def test_insert_between_first_five_twelve_sixteen_twenty_second_none_success():
    # Setup
    values0: list[int] = [5, 12, 16, 20]
    values1: list[int] = [12, 16]
    values2: list[int] = [5, 20]
    head0: Node = nodes_from_values(values=values0)
    head1: None = None
    head2: Node = nodes_from_values(values=values2)
    before0: Node = head0
    after0: Node = head0.previous
    insert0: None = head1
    removed0: Node = nodes_from_values(values=values1)

    # Execution
    inserted0: Node = insert_between(before=before0, after=after0, insert=insert0)

    # Validation
    assert equal(first=inserted0, second=removed0)
    assert equal(first=head0, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=inserted0) is True
    assert is_value_at_index(node=head0, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True
    assert is_value_at_index(node=removed0, reference=values1) is True


def test_insert_between_first_three_seven_nine_fifteen_nineteen_second_ten_twelve_two_five_without_head_failure():
    # Setup
    head0: Node = nodes_from_values(values=[3, 7, 9, 15, 19])
    head1: Node = nodes_from_values(values=[10, 12, 2, 5])
    before0: Node = head0.next.next
    after0: Node = before0
    insert0: Node = head1

    # Validation
    with pytest.raises(NoNewHeadError):
        _: Node = insert_between(before=before0, after=after0, insert=insert0)


def test_insert_between_first_three_seven_nine_fifteen_nineteen_second_ten_twelve_two_five_with_head_success():
    # Setup
    values0: list[int] = [3, 7, 9, 15, 19]
    values1: list[int] = [10, 12, 2, 5]
    values2: list[int] = [2, 5, 9, 10, 12]
    values3: list[int] = [15, 19, 3, 7]
    head0: Node = nodes_from_values(values=values0)
    head1: Node = nodes_from_values(values=values1)
    head2: Node = nodes_from_values(values=values2)
    head3: Node = head1.previous.previous
    before0: Node = head0.next.next
    after0: Node = before0
    insert0: Node = head1
    removed1: Node = nodes_from_values(values=values3)

    # Execution
    inserted0: Node = insert_between(before=before0, after=after0, insert=insert0, head=head3)

    # Validation
    assert equal(first=inserted0, second=removed1)
    assert equal(first=head3, second=head2)
    assert is_consistent(node=head0) is True
    assert is_consistent(node=head1) is True
    assert is_consistent(node=inserted0) is True
    assert is_value_at_index(node=head0, reference=values3) is True
    assert is_value_at_index(node=head1, reference=values2) is True
    assert is_value_at_index(node=head2, reference=values2) is True
    assert is_value_at_index(node=removed1, reference=values3) is True
