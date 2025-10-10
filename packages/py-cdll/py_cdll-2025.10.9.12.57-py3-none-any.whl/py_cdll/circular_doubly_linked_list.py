from enum import Enum, auto
from typing import Sequence, Generic, TypeVar, MutableSequence, Iterable, overload, Callable, Any, Iterator

from .node import Node, merge_sort, reverse_order, insert_between, length, remove, nodes, update_head
from .compare import Comparison, compare
from .exceptions import ValueNotFoundError, MultipleValuesFoundError, \
    NoAdjacentValueError, NegativeIndexError, UnevenListLengthError, EmptyCDLLError, \
    FirstValueNotFoundError, SecondValueNotFoundError, ValuesNotAdjacentError, InputNotIterableError, \
    NoBeforeAndAfterUniqueError, CDLLAlreadyPopulatedError, UnableToPopulateWithNoValuesError, NotANodeError


class Connectivity(Enum):
    ADJACENT_NEXT = auto()
    ADJACENT_PREVIOUS = auto()

    def __invert__(self) -> "Connectivity":
        opposite_connectivity: dict[Connectivity, Connectivity] = {
            Connectivity.ADJACENT_NEXT: Connectivity.ADJACENT_PREVIOUS,
            Connectivity.ADJACENT_PREVIOUS: Connectivity.ADJACENT_NEXT}

        inverted_value: Connectivity = opposite_connectivity[self]

        return inverted_value


_T = TypeVar("_T")
_U = TypeVar("_U")


class CDLL(MutableSequence[_T], Generic[_T]):

    def __init__(self, values: Sequence[_T] | None = None) -> None:
        self._head: Node | None = None

        if values is not None and len(values) > 0:
            self._populate(values=values)

    @property
    def _last(self) -> Node:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find last in empty CDLL.")

        return self._head.previous

    def __repr__(self) -> str:
        values: list[str] = [repr(node.value) for node in self._nodes()]
        string: str = f"CDLL(...{id(self) % 1000000})[{len(self)}, [{', '.join(values)}]]"
        return string

    def __str__(self) -> str:
        values: list[str] = [repr(node.value) for node in self._nodes()]
        string: str = f"CDLL[{', '.join(values)}]"
        return string

    def is_empty(self) -> bool:
        is_head_none: bool = self._head is None
        is_empty: bool = True if is_head_none else False
        return is_empty

    def _add(self, first: Iterable[_T] | None, second: Iterable[_U] | None, is_inplace: bool) -> "CDLL[_T | _U]":
        if not isinstance(first, Iterable):
            raise TypeError(f"Can only concatenate an Iterable (not '{type(first)}') to '{type(self)}'.")
        if not isinstance(second, Iterable):
            raise TypeError(f"Can only concatenate an Iterable (not '{type(second)}') to '{type(self)}'.")

        cdll: CDLL[_T | _U] = self if is_inplace else CDLL()

        if not is_inplace:
            try:
                cdll.extend(values=first)
            except EmptyCDLLError:
                pass  # When cdll is empty, there is nothing to add to the new cdll

        try:
            cdll.extend(values=second)
        except EmptyCDLLError:
            pass  # When cdll is empty, there is nothing to add to the new cdll

        return cdll

    def __add__(self, other: Iterable[_U]) -> "CDLL[_T | _U]":
        new_list: CDLL[_T | _U] = self._add(first=self, second=other, is_inplace=False)

        return new_list

    def __radd__(self, other: Iterable[_U]) -> "CDLL[_T | _U]":
        new_list: CDLL[_T | _U] = self._add(first=other, second=self, is_inplace=False)

        return new_list

    def __iadd__(self, other: Iterable[_U]) -> "CDLL[_T | _U]":
        new_list: CDLL[_T | _U] = self._add(first=self, second=other, is_inplace=True)

        return new_list

    def __mul__(self, other: int) -> "CDLL[_T]":
        if not isinstance(other, int):
            raise TypeError(f"List repetition is only possible with integers, not '{type(other)}'.")

        new_list: CDLL[_T] = CDLL()

        if other > 0:
            for _ in range(other):
                new_list.extend(values=self)

        return new_list

    def __rmul__(self, other: int) -> "CDLL[_T]":
        new_list: CDLL[_T] = self.__mul__(other=other)
        return new_list

    def __imul__(self, other: int) -> "CDLL[_T]":
        if not isinstance(other, int):
            raise TypeError(f"List repetition is only possible with integers, not '{type(other)}'.")

        if other > 1:
            values: CDLL[_T] = self[:len(self)]
            for _ in range(other - 1):
                self.extend(values=values)
        elif other == 1:
            pass
        elif other < 1:
            self.clear()

        return self

    @property
    def head(self) -> _T:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find head in empty CDLL.")

        return self._head.value

    @property
    def last(self) -> _T:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find last in empty CDLL.")

        return self._last.value

    def _node_remove(self, target: Node) -> None:
        if len(self) > 1:
            # Set new head before removing node to prevent head from temporarily pointing to a node
            # that is no longer in the correct list.
            if target is self._head:
                self._head = self._head.next

            _ = remove(target=target)
        else:
            self.clear()

    def _node_remove_at_index(self, index: int) -> Node:
        target: Node = self._node_at_index(index=index)
        self._node_remove(target=target)
        return target

    # TODO: combine with _nodes_reverse() and add argument "reverse: bool = False" to select between them.
    def _nodes(self) -> Iterator[Node]:
        if self.is_empty():
            return

        for node in nodes(head=self._head, callback=lambda: self._head):
            yield node

    def _nodes_reverse(self) -> Iterator[Node]:
        if self.is_empty():
            return

        current: Node = self._last
        index: int = current.index

        while True:
            yield current

            index -= 1
            current = current.previous

            if current is self._last:
                break

    def _nodes_value(self,
                     value: _T,
                     comparison: Comparison = Comparison.IDENTITY_OR_EQUALITY
                     ) -> Iterator[Node]:

        for node in self._nodes():
            is_comparable: bool = compare(pair=(value, node.value), comparison=comparison)

            if is_comparable:
                yield node

    def _nodes_index(self, indices: list[int], reverse: bool = False) -> Iterator[Node]:
        indices.sort(reverse=reverse)

        if reverse:
            iterator: Iterator[Node] = self._nodes_reverse()
        else:
            iterator: Iterator[Node] = self._nodes()

        for node in iterator:
            while len(indices) > 0 and indices[0] == node.index:
                yield node
                indices = indices[1:]

    def _nodes_value_constrained(self,
                                 value: _T,
                                 start: int = 0,
                                 stop: int | None = None,
                                 comparison: Comparison = Comparison.IDENTITY_OR_EQUALITY
                                 ) -> Iterator[Node]:

        if start < 0:
            start = max(len(self) + start, 0)

        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop = max(len(self) + stop, 0)

        if start == stop:
            return

        for node in self._nodes():
            if start <= node.index <= stop:
                is_comparable: bool = compare(pair=(value, node.value), comparison=comparison)

                if is_comparable:
                    yield node

    def _node_unique(self, value: _T, comparison: Comparison = Comparison.IDENTITY) -> Node:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find value in empty CDLL.")

        unique_amount: int = 0
        unique_node: Node | None = None

        for node in self._nodes_value(value=value, comparison=comparison):
            unique_amount += 1
            unique_node = node

        if unique_amount < 1:
            raise ValueNotFoundError(f"No instance of value found.")
        elif unique_amount > 1:
            raise MultipleValuesFoundError(f"More than one instance of value found.")

        return unique_node

    def _node_first(self, value: _T, comparison: Comparison = Comparison.IDENTITY_OR_EQUALITY) -> Node:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find value in empty CDLL.")

        try:
            node = next(self._nodes_value(value=value, comparison=comparison))
        except StopIteration as exception:
            raise ValueNotFoundError(f"No instance of value found") from exception

        return node

    def index_unique(self, value: _T) -> int:
        node: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY)
        return node.index

    def index(self, value: _T, start: int = 0, stop: int | None = None) -> int:
        if start < 0:
            start = max(len(self) + start, 0)

        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop = max(len(self) + stop, 0)

        try:
            node: Node = next(self._nodes_value_constrained(value=value,
                                                            start=start,
                                                            stop=stop,
                                                            comparison=Comparison.IDENTITY_OR_EQUALITY))
        except StopIteration as exception:
            raise ValueError(f"Value '{value}' not in list, so there is no index to return.") from exception

        return node.index

    # TODO: add "steps: int", to select multiple steps before unique, defaulting to 1
    def before_unique(self, value: _T) -> _T:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find value in empty CDLL.")
        elif len(self) < 2:
            raise NoAdjacentValueError(f"No unique adjacent value when length is less than 2.")

        node: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY)

        return node.previous.value

    # TODO: add "steps: int", to select multiple steps after unique, defaulting to 1
    def after_unique(self, value: _T) -> _T:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find value in empty CDLL.")
        elif len(self) < 2:
            raise NoAdjacentValueError(f"No unique adjacent value when length is less than 2.")

        node: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY)

        return node.next.value

    def before_and_after_unique(self, value: _T) -> tuple[_T, _T]:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find value in empty CDLL.")
        elif len(self) < 3:
            raise NoAdjacentValueError(f"No unique adjacent value when length is less than 3.")

        try:
            node: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY)
        except (ValueNotFoundError, MultipleValuesFoundError) as exception:
            raise NoBeforeAndAfterUniqueError(f"Could not get values around element in CDLL.") from exception

        before: _T = node.previous.value
        after: _T = node.next.value

        return before, after

    def opposite_unique(self, value: _T) -> _T:
        is_length_even: bool = len(self) % 2 == 0

        if not is_length_even:
            raise UnevenListLengthError(f"No opposite item in list of uneven length.")

        half_length: int = len(self) // 2
        value_index: int = self.index_unique(value=value)
        opposite_index: int = self._wraparound_index(index=value_index + half_length)
        opposite: _T = self[opposite_index]

        return opposite

    def replace_unique(self, value: _T, replacement: _U) -> None:
        target: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY)
        replace: Node = Node(value=replacement)
        self._node_replace(target=target, replacement=replace)

    def replace_before_unique(self, value: _T, replacement: _U) -> None:
        if len(self) == 1:
            raise NoAdjacentValueError(f"No value before input in list of length 1.")

        target = self._node_unique(value=value, comparison=Comparison.IDENTITY).previous
        replace: Node = Node(value=replacement)
        self._node_replace(target=target, replacement=replace)

    def replace_after_unique(self, value: _T, replacement: _U) -> None:
        if len(self) == 1:
            raise NoAdjacentValueError(f"No value after input in list of length 1.")

        target: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY).next
        replace: Node = Node(value=replacement)
        self._node_replace(target=target, replacement=replace)

    def remove(self, value: _T) -> None:
        try:
            node = self._node_first(value=value, comparison=Comparison.IDENTITY_OR_EQUALITY)
        except ValueNotFoundError as exception:
            raise ValueError(f"Value '{value}' not in list, so there is nothing to remove.") from exception

        self._node_remove(target=node)

    def remove_unique(self, value: _T) -> None:
        node: Node = self._node_unique(value=value, comparison=Comparison.IDENTITY)
        self._node_remove(target=node)

    def pop(self, index: int | None = None) -> _T:
        if index is None:
            index = self._last.index

        try:
            target: Node = self._node_remove_at_index(index=index)
        except EmptyCDLLError as exception:
            raise IndexError(f"Can't pop a value from an empty cdll.") from exception

        value: _T = target.value

        return value

    def count(self, value: _T) -> int:
        iterator: Iterator[Node] = self._nodes_value(value=value, comparison=Comparison.IDENTITY_OR_EQUALITY)
        amount: int = sum(1 for _ in iterator)
        return amount

    def sort(self, key: Callable[[_T], Any] | None = None, reverse: bool = False) -> None:
        if self.is_empty():
            # If head is None, there is nothing to sort.
            return

        head: Node = self._head

        if key is None:
            self._head = merge_sort(head=head)
        else:
            try:
                decorated: CDLL[tuple[Any, _T]] = CDLL(values=[(key(item), item) for item in self])
            except (KeyError, TypeError) as exception:
                raise exception

            decorated.sort()
            undecorated: CDLL[_T] = CDLL(values=[item for _, item in decorated])
            self._head = undecorated._head

        if reverse:
            self._head = reverse_order(head=self._head)

    def __copy__(self) -> "CDLL[_T]":
        duplicate: CDLL[_T] = CDLL()
        duplicate.extend(values=self)
        return duplicate

    def copy(self) -> "CDLL[_T]":
        duplicate: CDLL[_T] = self.__copy__()
        return duplicate

    # TODO: Evaluate for removal
    def adjacent(self, pair: tuple[_T, _U]) -> bool:
        # TODO: raise exception if length is <2

        is_nodes_adjacent: bool = False

        try:
            value0_node = self._node_unique(value=pair[0], comparison=Comparison.IDENTITY)
        except ValueNotFoundError:
            return is_nodes_adjacent

        is_value0_next_value1: bool = value0_node.next.value is pair[1]
        is_value0_previous_value1: bool = value0_node.previous.value is pair[1]
        is_nodes_adjacent = is_value0_next_value1 or is_value0_previous_value1

        return is_nodes_adjacent

    # TODO: Evaluate for removal
    def adjacency_direction(self, pair: tuple[_T, _U]) -> Connectivity:
        # Direction from first towards second, if adjacent
        connectivity: Connectivity | None = None

        try:
            first_node = self._node_unique(value=pair[0], comparison=Comparison.IDENTITY)
        except ValueNotFoundError as exception:
            raise FirstValueNotFoundError(f"First value not found in CDLL.") from exception

        if first_node.next.value is pair[1]:
            connectivity: Connectivity = Connectivity.ADJACENT_NEXT
        elif first_node.previous.value is pair[1]:
            connectivity: Connectivity = Connectivity.ADJACENT_PREVIOUS

        try:
            second_node = self._node_unique(value=pair[1], comparison=Comparison.IDENTITY)
        except ValueNotFoundError as exception:
            raise SecondValueNotFoundError(f"Second value not found in CDLL.") from exception

        if first_node and second_node and not connectivity:
            raise ValuesNotAdjacentError(f"'{pair[0]}' and '{pair[1]}' are not adjacent in '{self}'.")

        return connectivity

    def _populate(self, values: Sequence[_T]) -> None:
        if self.is_empty():
            values_iterator: Iterator[_T] = iter(values)

            try:
                self._head = Node(value=next(values_iterator))
            except StopIteration as exception:
                raise UnableToPopulateWithNoValuesError(f"Unable to populate CDLL "
                                                        f"from an empty Sequence") from exception

            self.extend(values=values_iterator)
        else:
            raise CDLLAlreadyPopulatedError(f"Unable to populate CDLL "
                                            f"as there is already '{len(self)}' elements in it.")

    def append(self, value: _T) -> None:
        if self.is_empty():
            self._populate(values=[value])
        else:
            insert: Node = Node(value=value)
            self._insert_after_node(anchor=self._last, insert=insert)

    def extend(self, values: Iterable[_T] | Sequence[_T]) -> None:
        try:
            for value in values:
                self.append(value=value)
        except TypeError as exception:
            raise InputNotIterableError(f"Input contains no value that can be appended to CDLL.") from exception

    def insert(self, index: int, value: _T) -> None:
        if self.is_empty():
            self._populate(values=[value])
        else:
            self._insert(index=index, value=value)

    def clear(self) -> None:
        self._head = None

    # TODO: Evaluate for removal
    def _shift_head_forwards(self, amount: int = 1) -> None:
        # TODO: generalise shift head to take positive and negative
        # TODO: raise exception when cdll does not have even length
        #       can't seem to remember reason why that would be necessary in all cases...
        if self.is_empty():
            raise EmptyCDLLError(f"Not possible to shift head in empty CDLL.")

        if amount <= 0:
            raise ValueError(f"Amount to shift '{amount}' must be a positive integer")

        new_head: Node = self._head

        for _ in range(amount):
            new_head = new_head.next

        update_head(node=new_head)
        self._head = new_head

    # TODO: Evaluate for removal
    def _shift_head_backwards(self, amount: int = 1) -> None:
        # TODO: raise exception when cdll does not have even length
        #       can't seem to remember reason why that would be necessary in all cases...
        if self.is_empty():
            raise EmptyCDLLError(f"Not possible to shift head in empty CDLL.")

        if amount <= 0:
            raise ValueError(f"Amount to shift '{amount}' must be a positive integer")

        new_head: Node = self._head

        for _ in range(amount):
            new_head = new_head.previous

        update_head(node=new_head)
        self._head = new_head

    # TODO: Evaluate for removal
    def rotate(self, amount: int = 0) -> None:
        if amount == 0:
            pass
        elif amount > 0:
            self._shift_head_backwards(amount=amount)
        elif amount < 0:
            self._shift_head_forwards(amount=abs(amount))

    def _node_at_index(self, index: int) -> Node:
        if self.is_empty():
            raise EmptyCDLLError(f"Impossible to find value in empty CDLL.")

        index = self._normalize_index(index=index)

        for node in self._nodes():
            if node.index == index:
                current: Node = node
                break
        else:
            raise IndexError(f"Index '{index}' not in range of '{len(self)}'.")

        return current

    @staticmethod
    def _insert_after_node(anchor: Node, insert: Node) -> None:
        insert_between(before=anchor, after=anchor.next, insert=insert)

    def _insert_before_node(self, anchor: Node, insert: Node) -> None:
        self._insert_after_node(anchor=anchor.previous, insert=insert)
        if anchor is self._head:
            update_head(node=insert)
            self._head = insert

    def _node_replace(self, target: Node, replacement: Node) -> None:
        is_target_head: bool = target is target.head

        if len(self) > 1:
            head: Node | None = None
            if is_target_head:
                head = replacement

            _ = insert_between(before=target.previous, after=target.next, insert=replacement, head=head)

        if is_target_head:
            self._head = replacement

    def _replace_at_index(self, index: int, replacement: _U) -> None:
        # Imitates list behavior which raises an exception for any non-filled index.
        if self.is_empty():
            raise IndexError(f"Index value of '{index}' is not in range of size '({-len(self)}:)0:{len(self) - 1}'")
        else:
            target: Node = self._node_at_index(index=index)
            replacement: Node = Node(value=replacement)
            self._node_replace(target=target, replacement=replacement)

    def _replace_with_slice(self, segment: slice, values: Sequence[_U]) -> None:
        section: range = self._range_from_slice(segment=segment)
        indices: list[int] = list(section)
        are_indices_consecutive: bool = self._are_consecutive(numbers=indices)

        if are_indices_consecutive:
            for index in reversed(indices):
                self._node_remove_at_index(index=index)
            for value in reversed(values):
                try:
                    self._insert(index=section.start, value=value)
                except IndexError:
                    self.append(value=value)
        else:
            if len(indices) == len(values):
                for node, value in zip(self._nodes_index(indices=indices), values):
                    replacement: Node = Node(value=value)
                    self._node_replace(target=node, replacement=replacement)
            else:
                raise ValueError(f"attempt to assign sequence of size '{len(values)}' "
                                 f"to extended slice of size '{len(indices)}'.")

    def _remove_with_slice(self, segment: slice) -> None:
        indices: list[int] = list(self._range_from_slice(segment=segment))
        indices.sort()

        for index in reversed(indices):
            self._node_remove_at_index(index=index)

    def _range_from_slice(self, segment: slice) -> range:
        start, stop, step = segment.indices(len(self))
        indices: range = range(start, stop, step)
        return indices

    @staticmethod
    def _are_consecutive(numbers: Sequence[int]) -> bool:
        are_consecutive: list[bool] = [numbers[index] + 1 == numbers[index + 1] for index in range(len(numbers) - 1)]
        are_all_consecutive: bool = all(are_consecutive)
        return are_all_consecutive

    def _insert(self, index: int, value: _T) -> None:
        # Imitates list behavior which inserts any index for an empty list at index zero,
        # and appends for any index out of range.
        if self.is_empty():
            self._populate(values=[value])
        else:
            try:
                node_current = self._node_at_index(index=index)
                node_new = Node(value=value)
                self._insert_before_node(anchor=node_current, insert=node_new)
            except IndexError:
                self.append(value=value)

    def __len__(self) -> int:
        try:
            length_: int = length(node=self._head)
        except NotANodeError:
            length_: int = 0

        return length_

    def _normalize_index(self, index: int) -> int:
        if index < -len(self) or index >= len(self):
            # IndexError used by python loops to know when end of iterable has been reached
            raise IndexError(f"Index value of '{index}' is not in range of '({-len(self)}:)0:{len(self) - 1}'")

        if index < 0:
            index = index % len(self)

        return index

    def _wraparound_index(self, index: int) -> int:
        return index % len(self)

    def __eq__(self, other: "CDLL[_U]") -> bool:
        equal: bool = isinstance(other, type(self))

        if equal:
            equal &= len(self) == len(other)

            if equal:
                equal &= all(self_item is other_item or self_item == other_item
                             for self_item, other_item in zip(self, other))

        return equal

    # TODO: Evaluate for removal
    def _eq_rotated_mirrored(self, other: "CDLL[_U]") -> bool:
        # TODO: Do I really need the mirrored part of the check?
        # TODO: seems like this is broken when there are multiple items of the same in a list, and it is rotated
        #       then there is no guarantee that the find_first picks the correct of the two
        #       there would have to be a find_all method and a test against all the following items
        #       from each starting point until confirmed match, failure and go to next, or all failure

        self_length: int = len(self)

        if self_length == 0:
            return True

        # Shortcut for when both lists are uninitialized
        if self.is_empty() and other.is_empty():
            return True

        has_same_lengths: bool = self_length == len(other)
        has_same_items: bool = False

        if has_same_lengths:
            mirrored: bool = False
            connection_pair_equality: list[bool] = []

            start_item: _T = self.head
            other_start_index: int

            try:
                other_start_index = other.index(value=start_item)
            except ValueNotFoundError:
                return False

            # check start neighbors and their mirroring
            if self_length > 1:
                self_last: _T = self[-1]
                self_second: _T = self[1]

                other_last: _U = other[other._wraparound_index(index=other_start_index - 1)]
                other_second: _U = other[other._wraparound_index(index=other_start_index + 1)]

                all_none: bool = self_second is None and self_last is None and \
                                 other_second is None and other_last is None

                if self_second == other_last and self_last == other_second and not all_none:
                    mirrored = True

            connection_pairs: list[tuple[_T, _T]] = []
            for index, element in enumerate(self):
                if mirrored:
                    index_other: int = other._wraparound_index(index=other_start_index - index)
                else:
                    index_other: int = other._wraparound_index(index=other_start_index + index)
                connection_pairs.append((self[index], other[index_other]))

            for element0, element1 in connection_pairs:
                connection_pair_equality.append(element0 == element1)

            # TODO: change comparisons to be added up with &=
            has_same_items: bool = all(connection_pair_equality)

        return has_same_lengths and \
               has_same_items

    # TODO: Evaluate for removal
    def mirror(self, index: int = 0) -> None:
        # TODO: evaluate if the normalize call can be removed
        index = self._normalize_index(index=index)

        if index < 0:
            raise NegativeIndexError(f"Index '{index}' is not zero or greater")

        if index > 0:
            self._shift_head_forwards(amount=index)

        pair_amount: int = (len(self) - 1) // 2
        # pairs are first and last remaining indexes after index 0, narrowing inwards,
        # until zero or one unassigned indexes remain
        index_pairs: list[tuple[int, int]] = [(1 + index, len(self) - 1 - index) for index in range(pair_amount)]

        for pair in index_pairs:
            self.switch(pair=pair)

        if index > 0:
            self._shift_head_backwards(amount=index)

    # TODO: Evaluate for removal
    # TODO: if keep, create function for switching nodes instead of values
    def switch(self, pair: tuple[int, int]) -> None:
        self[pair[0]], self[pair[1]] = self[pair[1]], self[pair[0]]

    @overload
    def __getitem__(self, index: int) -> _T:
        ...

    @overload
    def __getitem__(self, index: slice) -> "CDLL[_T]":
        ...

    def __getitem__(self, index: int | slice) -> "_T | CDLL[_T]":
        if isinstance(index, int):
            value: _T = self._node_at_index(index=index).value
        elif isinstance(index, slice):
            value: CDLL[_T] = self._slice(segment=index)
        else:
            raise TypeError(f"__getitem__ requires an integer or a slice, not a {type(index)}.")
        return value

    @overload
    def __setitem__(self, index: int, value: _T) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[_T]) -> None:
        ...

    def __setitem__(self, index: int | slice, value: _T | Iterable[_T]) -> None:
        if isinstance(index, int):
            self._replace_at_index(index=index, replacement=value)
        elif isinstance(index, slice):
            self._replace_with_slice(segment=index, values=value)
        else:
            raise TypeError(f"__setitem__ requires an integer or a slice, not a {type(index)}.")

    def __delitem__(self, index: int | slice) -> None:
        if isinstance(index, int):
            _: Node = self._node_remove_at_index(index=index)
        elif isinstance(index, slice):
            self._remove_with_slice(segment=index)
        else:
            raise TypeError(f"__delitem__ requires an integer or a slice, not a {type(index)}.")

    def __contains__(self, value: _T) -> bool:
        contains: bool = True

        try:
            _ = self._node_first(value=value, comparison=Comparison.IDENTITY_OR_EQUALITY)
        except (EmptyCDLLError, ValueNotFoundError):
            contains = False

        return contains

    def __reversed__(self) -> Iterator[_T]:
        for node in self._nodes_reverse():
            yield node.value

    def __iter__(self) -> Iterator[_T]:
        for node in self._nodes():
            yield node.value

    def _slice(self, segment: slice) -> "CDLL[_T]":
        cdll: CDLL[_T] = CDLL()

        indices: range = self._range_from_slice(segment=segment)
        reverse: bool = True if indices.step < 0 else False

        for node in self._nodes_index(indices=list(indices), reverse=reverse):
            cdll.append(value=node.value)

        return cdll


# TODO: Evaluate for removal
CDLLPair = tuple[CDLL, CDLL]
CDLLPairs = list[CDLLPair]


if __name__ == '__main__':
    pass
