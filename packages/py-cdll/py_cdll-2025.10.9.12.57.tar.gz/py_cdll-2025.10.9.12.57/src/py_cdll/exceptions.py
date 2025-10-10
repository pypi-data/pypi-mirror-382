class BaseCDLLException(Exception):
    """Base exception for Circular Doubly Linked List project."""


class CDLLAlreadyPopulatedError(BaseCDLLException):
    """Raise when attempting to populate CDLL, but there is already data in it."""


class NegativeIndexError(BaseCDLLException):
    """Raise for indices that should be at least 0."""


class IndexNotFoundError(BaseCDLLException):
    """Raise for indices that are not found."""


class IndexOutOfRangeError(BaseCDLLException):
    """Raise for indices that are too high to appear in sequence."""


class ValueNotFoundError(BaseCDLLException):
    """Raise for searches that return no result."""


class FirstValueNotFoundError(BaseCDLLException):
    """Raise when the first input of a method was not found where expected."""


class SecondValueNotFoundError(BaseCDLLException):
    """Raise when the second input of a method was not found where expected."""


class ValuesNotAdjacentError(BaseCDLLException):
    """Raise when values were not found adjacent to each other."""


class NoAdjacentValueError(BaseCDLLException):
    """Raise for searches for adjacent values in lists with single item."""


class MultipleValuesFoundError(BaseCDLLException):
    """Raise for searches that return no result."""


class UnableToPopulateWithNoValuesError(BaseCDLLException):
    """Raise when attempting to populate CDLL without any values."""


class EmptyCDLLError(BaseCDLLException):
    """Raise when an iterable is found to be empty."""


class UnevenListLengthError(BaseCDLLException):
    """Raise for lists that contain uneven amount of items."""


class InputNotIterableError(BaseCDLLException):
    """Raise when an input is not iterable."""


class NoBeforeAndAfterUniqueError(BaseCDLLException):
    """Raise when it is impossible to return the values before and after a unique element."""


class NoOrderedOccurrenceError(BaseCDLLException):
    """Raise when it is impossible to tell if data is ordered because values are missing."""


class NotANodeError(BaseCDLLException):
    """Raise when a supposed Node turns out not to be so."""


class NodesNotInSameListError(BaseCDLLException):
    """Raise when two Nodes are not in the same list."""


class NoNewHeadError(BaseCDLLException):
    """Raise when no new head is provided for Node sequence."""
