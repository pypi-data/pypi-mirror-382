from typing import Callable

import pytest

from src.py_cdll import CDLL


def test_sort_integers_success():
    # Setup
    list0: list[int] = [71, 52, 28, 33, 35, 25, 70, 36, 27, 6]
    list1: list[int] = [6, 25, 27, 28, 33, 35, 36, 52, 70, 71]
    cdll0: CDLL[int] = CDLL(values=list0)
    cdll1: CDLL[int] = CDLL(values=list1)

    # Execution
    cdll0.sort()

    # Validation
    assert cdll0 == cdll1


def test_sort_strings_success():
    # Setup
    # noinspection SpellCheckingInspection
    list0: list[str] = ['glpwi', 'atmev', 'rlcar', 'ayupu', 'nezfv', 'xdeur', 'tpdht', 'lrcjt', 'odswj', 'cdzyo']
    # noinspection SpellCheckingInspection
    list1: list[str] = ['atmev', 'ayupu', 'cdzyo', 'glpwi', 'lrcjt', 'nezfv', 'odswj', 'rlcar', 'tpdht', 'xdeur']
    cdll0: CDLL[str] = CDLL(values=list0)
    cdll1: CDLL[str] = CDLL(values=list1)

    # Execution
    cdll0.sort()

    # Validation
    assert cdll0 == cdll1


def test_sort_functions_failure():
    # Setup
    list0: list[Callable] = [max, min, all, sorted, reversed, sum, any]
    cdll0: CDLL[Callable] = CDLL(values=list0)

    # Validation
    with pytest.raises(TypeError):
        cdll0.sort()


def test_sort_dict_key_correct_success():
    # Setup
    list0: list[dict[str, int]] = [{'age': 16, 'cats': 3}, {'age': 33, 'cats': 10}, {'age': 37, 'cats': 5},
                                   {'age': 43, 'cats': 6}, {'age': 26, 'cats': 10}, {'age': 80, 'cats': 0},
                                   {'age': 30, 'cats': 9}, {'age': 65, 'cats': 10}, {'age': 86, 'cats': 1}]
    list1: list[dict[str, int]] = [{'age': 16, 'cats': 3}, {'age': 26, 'cats': 10}, {'age': 30, 'cats': 9},
                                   {'age': 33, 'cats': 10}, {'age': 37, 'cats': 5}, {'age': 43, 'cats': 6},
                                   {'age': 65, 'cats': 10}, {'age': 80, 'cats': 0}, {'age': 86, 'cats': 1}]
    cdll0: CDLL[dict[str, int]] = CDLL(values=list0)
    cdll1: CDLL[dict[str, int]] = CDLL(values=list1)

    # Execution
    cdll0.sort(key=lambda x: x["age"])

    # Validation
    assert cdll0 == cdll1


def test_sort_dict_key_incorrect_failure():
    # Setup
    list0: list[dict[str, int]] = [{'age': 16, 'cats': 3}, {'age': 33, 'cats': 10}, {'age': 37, 'cats': 5},
                                   {'age': 43, 'cats': 6}, {'age': 26, 'cats': 10}, {'age': 80, 'cats': 0},
                                   {'age': 30, 'cats': 9}, {'age': 65, 'cats': 10}, {'age': 86, 'cats': 1}]
    cdll0: CDLL[dict[str, int]] = CDLL(values=list0)

    # Validation
    with pytest.raises(KeyError):
        cdll0.sort(key=lambda x: x["height"])


def test_sort_dict_key_not_subscriptable_failure():
    # Setup
    list0: list[Callable] = [max, min, all, sorted, reversed, sum, any]
    cdll0: CDLL[Callable] = CDLL(values=list0)

    # Validation
    with pytest.raises(TypeError):
        cdll0.sort(key=lambda x: x["some_key"])


def test_sort_integers_reversed_success():
    # Setup
    list0: list[int] = [71, 52, 28, 33, 35, 25, 70, 36, 27, 6]
    list1: list[int] = [71, 70, 52, 36, 35, 33, 28, 27, 25, 6]
    cdll0: CDLL[int] = CDLL(values=list0)
    cdll1: CDLL[int] = CDLL(values=list1)

    # Execution
    cdll0.sort(reverse=True)

    # Validation
    assert cdll0 == cdll1
