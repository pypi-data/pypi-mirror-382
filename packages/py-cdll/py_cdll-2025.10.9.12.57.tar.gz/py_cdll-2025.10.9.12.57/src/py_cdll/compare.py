from enum import Enum, auto
from typing import Any


class Comparison(Enum):
    EQUALITY = auto()
    IDENTITY = auto()
    IDENTITY_OR_EQUALITY = auto()


def compare_identity(pair: tuple[Any, Any]) -> bool:
    is_identical: bool = pair[0] is pair[1]
    return is_identical


def compare_equality(pair: tuple[Any, Any]) -> bool:
    is_equal: bool = pair[0] == pair[1]
    return is_equal


def compare(pair: tuple[Any, Any], comparison: Comparison) -> bool:
    is_comparable: bool = False

    match comparison:
        case Comparison.IDENTITY:
            is_comparable = compare_identity(pair=pair)
        case Comparison.EQUALITY:
            is_comparable = compare_equality(pair=pair)
        case Comparison.IDENTITY_OR_EQUALITY:
            is_comparable = compare_identity(pair=pair) or compare_equality(pair=pair)

    return is_comparable
