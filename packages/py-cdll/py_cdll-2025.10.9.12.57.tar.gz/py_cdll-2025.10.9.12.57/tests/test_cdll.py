import pytest

from src.py_cdll.circular_doubly_linked_list import CDLL, Connectivity
from src.py_cdll.exceptions import EmptyCDLLError, FirstValueNotFoundError, \
    SecondValueNotFoundError, ValuesNotAdjacentError
from src.py_cdll.node import is_consistent, is_value_at_index


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


def test_shift_head_forwards_empty_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        cdll0._shift_head_forwards()


def test_shift_head_forwards_with_full_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data1, data2, data0]
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._shift_head_forwards()

    # Validation
    assert cdll0.head == data1
    assert cdll0.last == data0
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test_shift_head_forwards_multiple_with_full_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data2, data0, data1]
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._shift_head_forwards(5)

    # Validation
    assert cdll0.head == data2
    assert cdll0.last == data1
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test_shift_head_forwards_zero_amount_with_full_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(ValueError):
        cdll0._shift_head_forwards(0)


def test_shift_head_forwards_negative_amount_with_full_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(ValueError):
        cdll0._shift_head_forwards(-1)


########################################################################################################################


def test_shift_head_backwards_empty_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        cdll0._shift_head_backwards()


def test_shift_head_backwards_with_full_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data2, data0, data1]
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._shift_head_backwards()

    # Validation
    assert cdll0.head == data2
    assert cdll0.last == data1
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test_shift_head_backwards_multiple_with_full_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    values1: list[str] = [data1, data2, data0]
    cdll0: CDLL = CDLL(values=values0)

    # Execution
    cdll0._shift_head_backwards(5)

    # Validation
    assert cdll0.head == data1
    assert cdll0.last == data0
    assert cdll0._head is cdll0._head.head
    assert is_consistent(node=cdll0._head)
    assert is_value_at_index(node=cdll0._head, reference=values1)


def test_shift_head_backwards_zero_amount_with_full_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(ValueError):
        cdll0._shift_head_backwards(0)


def test_shift_head_backwards_negative_amount_with_full_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    values0: list[str] = [data0, data1, data2]
    cdll0: CDLL = CDLL(values=values0)

    # Validation
    with pytest.raises(ValueError):
        cdll0._shift_head_backwards(-1)


########################################################################################################################


def test_rotate_none_success():
    # Setup
    data0: str = "0"
    data1: str = "1"
    data2: str = "2"
    data3: str = "3"
    data4: str = "4"
    values0: list[str] = [data0, data1, data2, data3, data4]
    cdll0: CDLL = CDLL(values=values0)
    cdll1: CDLL = CDLL(values=values0)

    # Validation
    assert cdll0 == cdll1


def test_rotate_positive_one_success():
    # Setup
    data0: str = "0"
    data1: str = "1"
    data2: str = "2"
    data3: str = "3"
    data4: str = "4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)
    cdll1: CDLL = CDLL()
    cdll1.append(data1)
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)
    cdll1.append(data0)

    # Execution
    cdll1.rotate(amount=1)

    # Validation
    assert cdll0 == cdll1


def test_rotate_positive_two_success():
    # Setup
    data0: str = "0"
    data1: str = "1"
    data2: str = "2"
    data3: str = "3"
    data4: str = "4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)
    cdll1: CDLL = CDLL()
    cdll1.append(data2)
    cdll1.append(data3)
    cdll1.append(data4)
    cdll1.append(data0)
    cdll1.append(data1)

    # Execution
    cdll1.rotate(amount=2)

    # Validation
    assert cdll0 == cdll1


def test_rotate_negative_one_success():
    # Setup
    data0: str = "0"
    data1: str = "1"
    data2: str = "2"
    data3: str = "3"
    data4: str = "4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)
    cdll1: CDLL = CDLL()
    cdll1.append(data4)
    cdll1.append(data0)
    cdll1.append(data1)
    cdll1.append(data2)
    cdll1.append(data3)

    # Execution
    cdll1.rotate(amount=-1)

    # Validation
    assert cdll0 == cdll1


def test_rotate_negative_two_success():
    # Setup
    data0: str = "0"
    data1: str = "1"
    data2: str = "2"
    data3: str = "3"
    data4: str = "4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)
    cdll1: CDLL = CDLL()
    cdll1.append(data3)
    cdll1.append(data4)
    cdll1.append(data0)
    cdll1.append(data1)
    cdll1.append(data2)

    # Execution
    cdll1.rotate(amount=-2)

    # Validation
    assert cdll0 == cdll1


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


def test_adjacent_with_adjacent_correct_order_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Execution
    is_adjacent: bool = cdll0.adjacent(pair=(data2, data3))

    # Validation
    assert is_adjacent


def test_adjacent_with_adjacent_incorrect_order_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Validation
    assert cdll0.adjacent(pair=(data4, data3)) is True


def test_adjacent_with_non_adjacent_correct_order_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Validation
    assert cdll0.adjacent(pair=(data1, data4)) is False


def test_adjacent_with_non_adjacent_incorrect_order_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL()
    cdll0.append(data0)
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Validation
    assert cdll0.adjacent(pair=(data3, data0)) is False


########################################################################################################################


def test_adjacency_direction_first_second_next_success():
    # Setup
    cdll0: CDLL = CDLL()
    data0: int = 0
    data1: int = 1
    cdll0.extend(values=[data0, data1])

    # Execution
    connectivity0: Connectivity = cdll0.adjacency_direction(pair=(data0, data1))

    # Validation
    assert connectivity0 is Connectivity.ADJACENT_NEXT


def test_adjacency_direction_second_first_previous_success():
    # Setup
    cdll0: CDLL = CDLL()
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    cdll0.extend(values=[data0, data1, data2, data3])

    # Execution
    connectivity0: Connectivity = cdll0.adjacency_direction(pair=(data0, data3))

    # Validation
    assert connectivity0 is Connectivity.ADJACENT_PREVIOUS


def test_adjacency_direction_separate_first_second_failure():
    # Setup
    cdll0: CDLL = CDLL()
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    cdll0.extend(values=[data0, data1, data2, data3, data4])

    # Validation
    with pytest.raises(ValuesNotAdjacentError):
        cdll0.adjacency_direction(pair=(data1, data3))


def test_adjacency_direction_separate_second_first_failure():
    # Setup
    cdll0: CDLL = CDLL()
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    cdll0.extend(values=[data0, data1, data2, data3, data4])

    # Validation
    with pytest.raises(ValuesNotAdjacentError):
        cdll0.adjacency_direction(pair=(data4, data2))


def test_adjacency_direction_missing_first_failure():
    # Setup
    cdll0: CDLL = CDLL()
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    data_missing: str = "missing"
    cdll0.extend(values=[data0, data1, data2, data3, data4])

    # Validation
    with pytest.raises(FirstValueNotFoundError):
        # noinspection PyTypeChecker
        cdll0.adjacency_direction(pair=(data_missing, data2))


def test_adjacency_direction_missing_second_failure():
    # Setup
    cdll0: CDLL = CDLL()
    data0: int = 0
    data1: int = 1
    data2: int = 2
    data3: int = 3
    data4: int = 4
    data_missing: str = "missing"
    cdll0.extend(values=[data0, data1, data2, data3, data4])

    # Validation
    with pytest.raises(SecondValueNotFoundError):
        # noinspection PyTypeChecker
        cdll0.adjacency_direction(pair=(data2, data_missing))


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


def test_mirror_empty_at_head_failure():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(IndexError):
        cdll0.mirror()


def test_mirror_single_item_at_head_success():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL(values=[data0])

    # Execution
    cdll0.mirror()

    # Validation
    assert cdll0.head == data0


def test_mirror_five_items_at_head_success():
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"

    cdll0: CDLL = CDLL(values=[data0])

    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Execution
    cdll0.mirror()

    # Validation
    assert list(cdll0) == [data0, data4, data3, data2, data1]


def test_mirror_six_items_at_index_two_success():
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"

    cdll0: CDLL = CDLL(values=[data0])

    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)
    cdll0.append(data5)

    index0: int = 2

    # Execution
    cdll0.mirror(index=index0)

    # Validation
    assert list(cdll0) == [data4, data3, data2, data1, data0, data5]


def test_mirror_six_items_at_index_minus_four_success():
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"

    cdll0: CDLL = CDLL(values=[data0])

    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)
    cdll0.append(data5)

    index0: int = -4

    # Execution
    cdll0.mirror(index=index0)

    # Validation
    assert list(cdll0) == [data4, data3, data2, data1, data0, data5]


########################################################################################################################


def test_switch_with_empty_index_out_of_bounds_success():
    # Setup
    cdll0: CDLL = CDLL()

    # Validation
    with pytest.raises(EmptyCDLLError):
        cdll0.switch(pair=(0, 0))


def test_switch_with_index_out_of_bounds_failure():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(data1)

    # Validation
    with pytest.raises(IndexError):
        cdll0.switch(pair=(0, 2))


def test_switch_with_single_item_success():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL(values=[data0])

    # Execution
    cdll0.switch(pair=(0, 0))

    # Validation
    assert cdll0[0] == data0


def test_switch_with_two_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(data1)

    # Execution
    cdll0.switch(pair=(0, 1))

    # Validation
    assert list(cdll0) == [data1, data0]


def test_switch_with_five_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Execution
    cdll0.switch(pair=(1, 3))

    # Validation
    assert list(cdll0) == [data0, data3, data2, data1, data4]


def test_switch_twice_with_five_items_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(data1)
    cdll0.append(data2)
    cdll0.append(data3)
    cdll0.append(data4)

    # Execution
    cdll0.switch(pair=(1, 3))
    cdll0.switch(pair=(2, 3))

    # Validation
    assert list(cdll0) == [data0, data3, data1, data2, data4]


########################################################################################################################


def test_equality_rotated_mirrored_empty_success():
    # Setup
    cdll0: CDLL = CDLL()
    cdll1: CDLL = CDLL()

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_one_element_success():
    # Setup
    data0: str = "data0"
    cdll0: CDLL = CDLL(values=data0)
    cdll1: CDLL = CDLL(values=data0)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_two_elements_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=data0)
    cdll0.append(value=data1)
    cdll1: CDLL = CDLL(values=data0)
    cdll1.append(value=data1)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_two_by_two_different_elements_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    cdll0: CDLL = CDLL(values=data0)
    cdll0.append(value=data1)
    cdll1: CDLL = CDLL(values=data2)
    cdll1.append(value=data3)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert not is_equal


def test_equality_rotated_mirrored_five_elements_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL(values=data0)
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll0.append(value=data3)
    cdll0.append(value=data4)
    cdll1: CDLL = CDLL(values=data0)
    cdll1.append(value=data1)
    cdll1.append(value=data2)
    cdll1.append(value=data3)
    cdll1.append(value=data4)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_two_elements_shifted_one_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(value=data1)
    cdll1: CDLL = CDLL(values=[data1])
    cdll1.append(value=data0)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_five_elements_shifted_three_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll0.append(value=data3)
    cdll0.append(value=data4)
    cdll1: CDLL = CDLL(values=[data3])
    cdll1.append(value=data4)
    cdll1.append(value=data0)
    cdll1.append(value=data1)
    cdll1.append(value=data2)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_seven_elements_shifted_four_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll0.append(value=data3)
    cdll0.append(value=data4)
    cdll0.append(value=data5)
    cdll0.append(value=data6)
    cdll1: CDLL = CDLL(values=[data4])
    cdll1.append(value=data5)
    cdll1.append(value=data6)
    cdll1.append(value=data0)
    cdll1.append(value=data1)
    cdll1.append(value=data2)
    cdll1.append(value=data3)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_three_elements_shifted_two_and_mirrored_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll1: CDLL = CDLL(values=[data2])
    cdll1.append(value=data1)
    cdll1.append(value=data0)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_five_elements_shifted_three_and_mirrored_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll0.append(value=data3)
    cdll0.append(value=data4)
    cdll1: CDLL = CDLL(values=[data3])
    cdll1.append(value=data2)
    cdll1.append(value=data1)
    cdll1.append(value=data0)
    cdll1.append(value=data4)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


def test_equality_rotated_mirrored_seven_elements_shifted_five_and_mirrored_success():
    # Setup
    data0: str = "data0"
    data1: str = "data1"
    data2: str = "data2"
    data3: str = "data3"
    data4: str = "data4"
    data5: str = "data5"
    data6: str = "data6"
    cdll0: CDLL = CDLL(values=[data0])
    cdll0.append(value=data1)
    cdll0.append(value=data2)
    cdll0.append(value=data3)
    cdll0.append(value=data4)
    cdll0.append(value=data5)
    cdll0.append(value=data6)
    cdll1: CDLL = CDLL(values=[data5])
    cdll1.append(value=data6)
    cdll1.append(value=data0)
    cdll1.append(value=data1)
    cdll1.append(value=data2)
    cdll1.append(value=data3)
    cdll1.append(value=data4)

    # Execution
    is_equal: bool = cdll0._eq_rotated_mirrored(other=cdll1)

    # Validation
    assert is_equal


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


if __name__ == '__main__':
    pass
