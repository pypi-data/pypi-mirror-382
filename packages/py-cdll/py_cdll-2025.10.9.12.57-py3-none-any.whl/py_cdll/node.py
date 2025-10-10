from typing import TypeVar, Iterator, Sequence, Callable

from .exceptions import NotANodeError, NodesNotInSameListError, NoNewHeadError, IndexNotFoundError, IndexOutOfRangeError

_T = TypeVar("_T")


class Node:
    """Circular Doubly Linked Node"""

    def __init__(self, value: _T) -> None:
        self.head: Node = self
        self.next: Node = self
        self.previous: Node = self
        self.index: int = 0
        self.value: _T = value

    def __repr__(self) -> str:
        values: list[str] = [repr(node.value) for node in nodes(head=self)]
        string = f"Node(...{id(self) % 1000000})[{length(node=self)}, {[self.value]}{values[1:]}]"
        return string


def nodes_from_values(values: Sequence[_T]) -> Node | None:
    """Create circular doubly linked list of Nodes containing values."""
    values_iterator: Iterator[_T] = iter(values)

    try:
        head: Node | None = Node(value=next(values_iterator))
        current: Node | None = head
    except StopIteration:
        head, current = None, None

    for value in values_iterator:
        node: Node = Node(value=value)
        insert_between(before=current, after=head, insert=node)
        current = current.next

    return head


def nodes(head: Node, callback: Callable[[], Node] | None = None) -> Iterator[Node]:
    current: Node = head
    steps: int = 0

    # TODO: might perform better with hasattr(callback, "__call__")
    is_callback_callable: bool = isinstance(callback, Callable)

    while True:
        yield current

        current = current.next
        steps += 1

        is_node_in_list: bool = current.head is callback() if is_callback_callable else current.head is head.head

        if not is_node_in_list:
            if callback:
                head = callback()
                new_current: Node = head
            else:
                new_current: Node = head.head

            for _ in range(steps):
                new_current = new_current.next

            if new_current.index != steps:
                break

            current = new_current

        if current is head:
            break


def is_consistent(node: Node) -> bool:
    is_correct: bool = True
    head: Node = node.head
    nodes__: list[Node] = []

    current: Node = head
    while True:
        nodes__.append(current)
        current = current.next
        if current is head:
            break

    for index, node in enumerate(nodes__):
        is_correct &= node.head is head
        is_correct &= node.index == index
        is_correct &= node.next.index == (node.index + 1) % len(nodes__)
        is_correct &= node.previous.index == (node.index - 1) % len(nodes__)
        is_correct &= node.next is nodes__[(index + 1) % len(nodes__)]
        is_correct &= node.previous is nodes__[(index - 1) % len(nodes__)]
        is_correct &= node.next.previous is node
        is_correct &= node.previous.next is node

        if not is_correct:
            break

    return is_correct


def node_with_index(node: Node, index: int) -> Node:
    if index >= length(node):
        raise IndexOutOfRangeError(f"Index '{index}' is out of range '{length(node) - 1}'.")

    head: Node = node.head
    current: Node = head

    while True:
        if current.index == index:
            break

        current = current.next

        if current is head:
            raise IndexNotFoundError(f"Index '{index}' not found in Node sequence.")

    return current


def is_value_at_index(node: Node, reference: list) -> bool:
    is_correct: bool = True

    if length(node=node) != len(reference):
        is_correct = False

    for index, value in enumerate(reference):
        try:
            node_at_index: Node = node_with_index(node=node, index=index)
            is_correct &= node_at_index.value == value
        except (IndexOutOfRangeError, IndexNotFoundError):
            is_correct = False

        if not is_correct:
            break

    return is_correct


def length_step(node: Node):
    """
    Count nodes in circular doubly linked sequence by stepping through a full round.
    Necessary in contexts where Node indices are not guaranteed to be correct.
    """

    current: Node = node
    amount: int = 0

    while True:
        amount += 1
        current = current.next
        if current is node:
            break

    return amount


def length(node: Node) -> int:
    """
    Calculates Node amount in circular doubly linked list by index of last Node.
    Assumes Node indices are correct.
    """

    try:
        length_: int = node.head.previous.index + 1
    except AttributeError as exception:
        raise NotANodeError(f"'{node}' is not a Node, but a '{type(node)}'.") from exception

    return length_


def remove(target: Node) -> Node:
    """
    Requires a minimum length of 2 nodes
    Assumes that target node is in a fully circular doubly linked list.
    """

    head: Node | None = None

    if target is target.head:
        head = target.next

    removed: Node = insert_between(before=target.previous, after=target.next, insert=None, head=head)

    return removed


def equal(first: Node, second: Node) -> bool:
    """Compare nodes from head in two circular doubly linked sequences."""
    equality: bool = True

    first_head: Node = first
    second_head: Node = second

    first_current: Node = first_head
    second_current: Node = second_head

    while True:
        equality &= first_current.value is second_current.value or first_current.value == second_current.value
        equality &= first_current.index == second_current.index
        equality &= first_current.head is first_head and second_current.head is second_head

        if not equality:
            break
        elif first_current.next is first_head and second_current.next is second_head:
            break
        elif first_current.next is first_head and second_current.next is not second_head:
            equality &= False
            break
        elif first_current.next is not first_head and second_current.next is second_head:
            equality &= False
            break

        first_current = first_current.next
        second_current = second_current.next

    return equality


def reverse_order(head: Node) -> Node:
    reversed_sequence: Node = head

    if head.next is not head:
        reversed_sequence: Node = head.previous
        previous_node: Node = head
        current_node: Node = head.previous

        while True:
            old_previous: Node = current_node.previous

            current_node.next = current_node.previous
            current_node.previous = previous_node

            previous_node = current_node
            current_node = old_previous

            if previous_node is head:
                break

    update_head(node=reversed_sequence)

    return reversed_sequence


def split_head_from_tail(node: Node) -> tuple[Node, Node | None]:
    first_head: Node = node

    if node.next is node:
        second_head: None = None
    else:
        second_head: Node = node.next
        split(first_head=first_head, second_head=second_head)

    return first_head, second_head


def middle_adjacent(head: Node) -> tuple[Node, Node]:
    """When node amount is uneven, preferentially adds one more node to before than after."""
    slow: Node = head
    fast: Node = head

    while fast.next is not head and fast.next.next is not head:
        slow = slow.next
        fast = fast.next.next

    before_last: Node = slow
    after_head: Node = slow.next

    return before_last, after_head


def stitch(head: Node, last: Node) -> None:
    """Stitch together head and last to make sequence circular."""
    head.previous, last.next = last, head


def split(first_head: Node, second_head: Node) -> None:
    """Split one circular doubly linked list into two."""

    if first_head.head is not second_head.head:
        raise NodesNotInSameListError(f"Nodes have different heads and are thus in different lists.")

    first_last: Node = second_head.previous
    second_last: Node = first_head.previous

    stitch(head=first_head, last=first_last), stitch(head=second_head, last=second_last)

    # TODO: refactor to extract repetitive code
    current: Node = first_head
    index: int = 0
    while True:
        current.head = first_head
        current.index = index

        current = current.next
        index += 1

        if current is first_head:
            break

    current: Node = second_head
    index: int = 0
    while True:
        current.head = second_head
        current.index = index

        current = current.next
        index += 1

        if current is second_head:
            break


def insert_between(before: Node, after: Node, insert: Node | None, head: Node | None = None) -> Node | None:
    """
    Insert sequence between before and after anchors. Return sequence previously between before and after anchors.
    Requires a minimum length of 1 Node.
    When working with 1 Node it is always going to assume that it should operate between its connections.
    Allows that insert can have multiple connected Nodes.
    Assumes that each input Node sequence is in a fully circular doubly linked list.
    """

    is_single_node_remaining: bool = before.index == after.index
    is_remaining_node_head: bool = before.index == 0
    is_new_head_provided: bool = head is not None

    if is_single_node_remaining and not is_remaining_node_head and not is_new_head_provided:
        raise NoNewHeadError(f"Expected new head, but none was provided.")

    is_node_amount_one: bool = length(node=before.head) == 1
    is_nothing_between_anchors: bool = before.next is after and after.previous is before

    if is_node_amount_one or is_nothing_between_anchors:
        removed_sequence_start: None = None
        removed_sequence_end: None = None
    else:
        removed_sequence_start: Node = before.next
        removed_sequence_end: Node = after.previous

    is_new_sequence_provided: bool = insert is not None
    is_sequence_to_be_removed: bool = removed_sequence_start is not None and removed_sequence_end is not None

    if is_new_sequence_provided:
        before_next: Node = insert
        after_previous: Node = insert.previous
    else:
        before_next: Node = after
        after_previous: Node = before

    if is_new_sequence_provided and is_sequence_to_be_removed:
        stitch(head=before_next, last=before), \
            stitch(head=after, last=after_previous), \
            stitch(head=removed_sequence_start, last=removed_sequence_end)
    elif not is_new_sequence_provided and is_sequence_to_be_removed:
        stitch(head=before_next, last=before), \
            stitch(head=removed_sequence_start, last=removed_sequence_end)
    elif is_new_sequence_provided and not is_sequence_to_be_removed:
        stitch(head=before_next, last=before), \
            stitch(head=after, last=after_previous)
    elif not is_new_sequence_provided and not is_sequence_to_be_removed:
        pass
    else:
        raise ValueError(f"Unclear how Node sequences should be re-stitched...")

    if is_new_head_provided:
        update_head(node=head)
    elif is_new_sequence_provided or is_sequence_to_be_removed:
        update_from(node=before_next)

    if is_sequence_to_be_removed:
        update_head(node=removed_sequence_start)

    return removed_sequence_start


def update_from(node: Node) -> None:
    """
    Updates head and indices from node to and including end of sequence.
    Assumes that Node connections are consistent and only head and indices needs to be updated.
    """

    current: Node = node

    if length_step(current) == 1:
        head: Node = current
    else:
        head: Node = current.previous.head

    if current is head:
        index: int = 0
    else:
        index: int = current.previous.index + 1

    while True:
        current.head = head
        current.index = index

        current = current.next
        index += 1

        if current is head:
            break


def update_head(node: Node) -> None:
    """Update all Nodes with new head."""

    current: Node = node
    index: int = 0

    while True:
        current.head = node
        current.index = index

        current = current.next
        index += 1

        if current is node:
            break


def before_target(current: Node, head: Node, target: Node) -> Node:
    """
    When last node value is still smaller than target value, then the last node is "before target".
    Assuming pre-sorted sub-lists.
    Assuming first head value is lower than or equal to insert head value.
    """

    while current.next.value <= target.value and current.next is not head:
        current = current.next

    return current


def split_in_middle(head: Node) -> tuple[Node, Node]:
    before_head: Node = head
    _, after_head = middle_adjacent(head=head)

    split(first_head=before_head, second_head=after_head)

    return before_head, after_head


def merge(first: Node, second: Node) -> Node:
    """
    Merge pre-sorted circular doubly linked nodes.
    Moving nodes from second into sorted positions in first.
    Assuming pre-sorted sub-lists.
    """

    if first.value > second.value:
        first, second = second, first

    before_insert: Node = first

    while second is not None:
        insert, second = split_head_from_tail(node=second)
        before_insert = before_target(current=before_insert, head=first, target=insert)
        insert_between(before=before_insert, after=before_insert.next, insert=insert)

    return first


def merge_sort(head: Node) -> Node:
    """Merge-sort implementation for circular doubly linked nodes."""

    if head.next is head:
        # When there is only one value, there is nothing to sort.
        merged_sorted: Node = head
    else:
        first, second = split_in_middle(head=head)
        first_sorted, second_sorted = merge_sort(head=first), merge_sort(head=second)
        merged_sorted: Node = merge(first=first_sorted, second=second_sorted)

    return merged_sorted
