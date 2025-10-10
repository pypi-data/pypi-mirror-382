import numpy as np
import pytest

import galgopy.selection.functional as f

ALL_FUNCTIONS = [
    f.elitist_selection,
    f.fitness_proportionate_selection,
    f.random_selection,
    f.rank_based_selection,
    f.stochastic_universal_sampling,
    f.tournament_selection,
]


REAL_TEST_SETS = [
    (
        np.random.random((4, 5)),
        np.random.uniform(-1, 1, 4),
    ),
    (
        np.random.random((4, 5)),
        np.random.random(4),
    ),
    (
        np.array(
            [
                [11, 12, 13, 14, 15],
                [21, 22, 23, 24, 25],
                [31, 32, 33, 34, 35],
                [41, 42, 43, 44, 45],
            ],
            dtype=np.float64,
        ),
        np.array([0.1, 0.2, 0.3, 0.4]),
    ),
]

NON_REAL_TEST_SETS = [
    (
        np.random.randint(-5, 6, (4, 5)),
        np.random.uniform(-1, 1, 4),
    ),
    (
        np.random.randint(0, 6, (4, 5)),
        np.random.random(4),
    ),
    (
        np.random.randint(0, 2, (4, 5), dtype=np.bool_),
        np.random.uniform(-1, 1, 4),
    ),
    (
        np.random.randint(0, 2, (4, 5), dtype=np.bool_),
        np.random.random(4),
    ),
    (
        np.random.random((4, 5)),
        np.random.randint(0, 6, (4, 5)),
    ),
]

TEST_SETS_FAULTY = [
    (
        np.random.random((4, 5)),
        np.random.random(3),
    ),
    (
        np.random.random((4, 5)),
        np.random.random(5),
    ),
]


@pytest.mark.parametrize("func", ALL_FUNCTIONS)
@pytest.mark.parametrize("population, fitness", REAL_TEST_SETS)
@pytest.mark.parametrize("parents_count", [1, 2, 3, 4, 20])
def test_general(func, population, fitness, parents_count):
    selection = func(
        population=population.copy(),
        fitness=fitness.copy(),
        parents_count=parents_count,
    )
    assert parents_count == len(selection) or len(population) == len(selection)
    assert population.dtype == selection.dtype


@pytest.mark.parametrize("func", ALL_FUNCTIONS)
@pytest.mark.parametrize("population, fitness", NON_REAL_TEST_SETS)
@pytest.mark.parametrize("parents_count", [1, 2, 3, 4, 20])
def test_general_failed(func, population, fitness, parents_count):
    try:
        func(
            population=population.copy(),
            fitness=fitness.copy(),
            parents_count=parents_count,
        )
        assert AssertionError
    except ValueError:
        assert True


@pytest.mark.parametrize("func", ALL_FUNCTIONS)
@pytest.mark.parametrize("population, fitness", TEST_SETS_FAULTY)
@pytest.mark.parametrize("parents_count", [1, 2, 3, 4, 20])
def test_general_failed_len(func, population, fitness, parents_count):
    try:
        func(
            population=population.copy(),
            fitness=fitness.copy(),
            parents_count=parents_count,
        )
        assert AssertionError
    except ValueError:
        assert True


@pytest.mark.parametrize("func", ALL_FUNCTIONS)
@pytest.mark.parametrize("population, fitness", REAL_TEST_SETS)
@pytest.mark.parametrize("parents_count", [0])
def test_general_failed_parents_count(func, population, fitness, parents_count):
    try:
        func(
            population=population.copy(),
            fitness=fitness.copy(),
            parents_count=parents_count,
        )
        assert AssertionError
    except ValueError:
        assert True
