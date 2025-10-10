import numpy as np
import pytest

import galgopy.crossover.functional as f

REAL_FUNCTIONS = [
    f.intermediate_recombination,
    f.whole_arithmetic_recombination,
]
OTHER_FUNCTIONS = [
    f.multi_point_crossover,
    f.one_point_crossover,
    f.uniform_crossover,
]


REAL_PARENTS = [
    np.random.random((4, 5)),
    np.random.uniform(-1, 1, (4, 5)),
    np.array(
        [
            [11, 12, 13, 14, 15],
            [21, 22, 23, 24, 25],
            [31, 32, 33, 34, 35],
            [41, 42, 43, 44, 45],
        ],
        dtype=np.float64,
    ),
]

NON_REAL_PARENTS = [
    np.random.randint(0, 6, (4, 5)),
    np.random.randint(-5, 6, (4, 5)),
    np.random.randint(0, 2, (4, 5), dtype=np.bool_),
]


@pytest.mark.parametrize("func", [*REAL_FUNCTIONS, *OTHER_FUNCTIONS])
@pytest.mark.parametrize("parents", REAL_PARENTS)
def test_all(func, parents):
    children = func(parents=parents.copy())
    assert parents.dtype == children.dtype
    assert len(children) >= 1


@pytest.mark.parametrize("func", OTHER_FUNCTIONS)
@pytest.mark.parametrize("parents", [*REAL_PARENTS, *NON_REAL_PARENTS])
def test_other(func, parents):
    children = func(parents=parents.copy())
    assert parents.dtype == children.dtype
    assert len(children) >= 1


@pytest.mark.parametrize("func", REAL_FUNCTIONS)
@pytest.mark.parametrize("parents", NON_REAL_PARENTS)
def test_real_failed(func, parents):
    try:
        func(parents=parents.copy())
        assert AssertionError
    except ValueError:
        assert True
