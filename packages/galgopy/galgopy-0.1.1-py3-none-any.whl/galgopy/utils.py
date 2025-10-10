"""Utilities and helper functions."""

from collections.abc import Callable
from functools import wraps

import numpy as np


def pick_two_parents(
    parents: np.ndarray[tuple[int, int], np.dtype[np.float64]],
) -> tuple[
    np.ndarray[tuple[int], np.dtype[np.float64]],
    np.ndarray[tuple[int], np.dtype[np.float64]],
]:
    """Randomly picks two parents.

    Args:
        parents: Parents.

    Returns:
        Picked parents.

    """
    parents_count = len(parents)
    parent1, parent2 = parents[
        np.random.choice(parents_count, 2, replace=parents_count < 2)
    ]
    return parent1, parent2


def random_segment_indices(chromosome_size: int) -> tuple[int, int]:
    """Select a random segment of the chromosome.

    Args:
        chromosome_size: Chromosome size.

    Returns:
        Start and end index of the segment.

    Raises:
        ValueError: Chromosome length error. The minimum length is 2 genes.

    """
    if chromosome_size < 2:
        raise ValueError("A chromosome must have at least two genes.")
    start = np.random.randint(0, chromosome_size - 1)
    end = np.random.randint(start + 2, chromosome_size + 1)
    return start, end


def chromosome_set_bounds(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    old_bounds: tuple[float, float] = (-1, 1),
    new_bounds: tuple[float, float] = (0, 1),
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Change the boundaries of the chromosome.

    Args:
        chromosome: Chromosome.
        old_bounds: Gene boundaries (min, max).
        new_bounds: New boundaries (min, max).

    Returns:
        Chromosome with new boundaries.

    """
    gene_min, gene_max = old_bounds
    new_min, new_max = new_bounds
    normalized = (chromosome - gene_min) / (gene_max - gene_min)
    scaled = new_min + normalized * (new_max - new_min)
    return scaled


def chromosome_to_bool(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    gene_bounds: tuple[float, float] = (-1, 1),
) -> np.ndarray[tuple[int], np.dtype[np.bool_]]:
    """Convert chromosome to boolean type representation.

    Args:
        chromosome: Chromosome.
        gene_bounds: Gene boundaries (min, max).

    Returns:
        Chromosome representations in boolean type.

    """
    return chromosome > np.mean(gene_bounds)


def chromosome_to_int(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    gene_bounds: tuple[float, float] = (-1, 1),
    int_bounds: tuple[int, int] = (-10, 10),
) -> np.ndarray[tuple[int], np.dtype[np.int64]]:
    """Convert chromosome to integer type representation.

    Args:
        chromosome: Chromosome.
        gene_bounds: Gene boundaries (min, max).
        int_bounds: Boundaries for intager representations (min, max).

    Returns:
        Chromosome representations in intager type.

    """
    scaled = chromosome_set_bounds(chromosome, gene_bounds, int_bounds)
    return np.round(scaled).astype(np.int64)


def chromosome_to_indices(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int], np.dtype[np.int64]]:
    """Convert a chromosome into a sequence (indices) representation.

    Args:
        chromosome: Chromosome.

    Returns:
        Cromosome representation as indices sequence.

    """
    return np.argsort(np.argsort(chromosome))


def validate_crossover_dtype(func: Callable) -> Callable:
    """Validate crossover function inputs dtype."""

    @wraps(func)
    def wrapper(parents: np.ndarray, *args, **kwargs) -> Callable:
        if parents.dtype != np.float64:
            raise ValueError("The 'dtype' of parents should be 'float64'.")
        return func(parents, *args, **kwargs)

    return wrapper


def validate_mutation_dtype(func: Callable) -> Callable:
    """Validate mutation function inputs dtype."""

    @wraps(func)
    def wrapper(chromosome: np.ndarray, *args, **kwargs) -> Callable:
        if chromosome.dtype != np.float64:
            raise ValueError("The 'dtype' of chromosome should be 'float64'.")
        return func(chromosome, *args, **kwargs)

    return wrapper


def validate_selection_dtype(func: Callable) -> Callable:
    """Validate selection function inputs dtype."""

    @wraps(func)
    def wrapper(
        population: np.ndarray, fitness: np.ndarray, *args, **kwargs
    ) -> Callable:
        if population.dtype != np.float64:
            raise ValueError("The 'dtype' of population should be 'float64'.")
        if fitness.dtype != np.float64:
            raise ValueError("The 'dtype' of fitness should be 'float64'.")
        return func(population, fitness, *args, **kwargs)

    return wrapper


def validate_selection_len(func: Callable) -> Callable:
    """Validate selection function inputs lengths."""

    @wraps(func)
    def wrapper(
        population: np.ndarray, fitness: np.ndarray, *args, **kwargs
    ) -> Callable:
        if len(population) != len(fitness):
            raise ValueError(
                "'population' and 'fitness' should be equal in length."
            )
        return func(population, fitness, *args, **kwargs)

    return wrapper


def validate_selection_parents_count(func: Callable) -> Callable:
    """Validate selection function parents_count."""

    @wraps(func)
    def wrapper(
        population: np.ndarray,
        fitness: np.ndarray,
        parents_count: int,
        *args,
        **kwargs,
    ) -> Callable:
        if parents_count < 1:
            raise ValueError("'parents_count' should be greater than 1.")
        return func(population, fitness, parents_count, *args, **kwargs)

    return wrapper
