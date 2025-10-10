"""Set of selection functions."""

import numpy as np

from galgopy.utils import (
    validate_selection_dtype,
    validate_selection_len,
    validate_selection_parents_count,
)


@validate_selection_len
@validate_selection_dtype
@validate_selection_parents_count
def elitist_selection(
    population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    parents_count: int = 2,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Elitist Selection.

    Args:
        population: Population.
        fitness: Fitness.
        parents_count: Number of parents to select.

    Returns:
        Selected parents.

    """
    # TODO: Add Worning if len(population) < parents_count
    indices = np.argsort(fitness)[-parents_count:]
    return population[indices]


@validate_selection_len
@validate_selection_dtype
@validate_selection_parents_count
def fitness_proportionate_selection(
    population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    parents_count: int = 2,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Fitness Proportionate Selection (FPS) / Roulette Wheel Selection.

    Args:
        population: Population.
        fitness: Fitness.
        parents_count: Number of parents to select.

    Returns:
        Selected parents.

    """
    population_size = len(population)
    probabilities = fitness - fitness.min()
    probabilities /= probabilities.sum()
    selection_indices = np.random.choice(
        population_size, parents_count, p=probabilities
    )
    return population[selection_indices]


@validate_selection_len
@validate_selection_dtype
@validate_selection_parents_count
def random_selection(
    population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    parents_count: int = 2,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Random Selection.

    Args:
        population: Population.
        fitness: Fitness.
        parents_count: Number of parents to select.

    Returns:
        Selected parents.

    """
    population_size = len(population)
    selection_indices = np.random.choice(
        population_size,
        parents_count,
        replace=population_size < parents_count,
    )
    return population[selection_indices]


@validate_selection_len
@validate_selection_dtype
@validate_selection_parents_count
def rank_based_selection(
    population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    parents_count: int = 2,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Rank-Based Selection.

    Args:
        population: Population.
        fitness: Fitness.
        parents_count: Number of parents to select.

    Returns:
        Selected parents.

    """
    population_size = len(population)
    ranks = np.argsort(np.argsort(fitness)) + 1
    probabilities = ranks / ranks.sum()
    selection_indices = np.random.choice(
        population_size, parents_count, p=probabilities
    )
    return population[selection_indices]


@validate_selection_len
@validate_selection_dtype
@validate_selection_parents_count
def stochastic_universal_sampling(
    population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    parents_count: int = 2,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Stochastic Universal Sampling (SUS).

    Args:
        population: Population.
        fitness: Fitness.
        parents_count: Number of parents to select.

    Returns:
        Selected parents.

    """
    positive_fitness = fitness - np.min(fitness)
    step = np.sum(positive_fitness) / parents_count
    start_pointer = np.random.uniform(0, step)
    pointers = start_pointer + np.arange(parents_count) * step

    cumulative_sum = np.cumsum(positive_fitness)
    selection_indices = np.searchsorted(cumulative_sum, pointers)
    return population[selection_indices]


@validate_selection_len
@validate_selection_dtype
@validate_selection_parents_count
def tournament_selection(
    population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    parents_count: int = 2,
    tournament_size: int = 3,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Tournament Selection.

    Args:
        population: Population.
        fitness: Fitness.
        parents_count: Number of parents to select.
        tournament_size: Number of participants in the tournament.

    Returns:
        Selected parents.

    """
    parents = []
    population_size = len(population)
    for _ in range(parents_count):
        tournament_indices = np.random.choice(
            population_size,
            tournament_size,
            replace=population_size < tournament_size,
        )
        best_index = tournament_indices[np.argmax(fitness[tournament_indices])]
        parents.append(population[best_index])
    return np.array(parents)
