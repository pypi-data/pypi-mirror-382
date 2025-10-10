"""Set of mutation functions."""

import numpy as np

from galgopy.utils import random_segment_indices, validate_mutation_dtype


@validate_mutation_dtype
def flip_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    gene_rate: float = 0.5,
    gene_bounds: tuple[float, float] = (-1, 1),
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Flip Mutation.

    Args:
        chromosome: Chromosome.
        gene_rate: Impact rate on gen.
        gene_bounds: Gene boundaries.

    Returns:
        Mutated chromosome.

    """
    lower, upper = gene_bounds
    mask = np.random.rand(len(chromosome)) < gene_rate
    chromosome[mask] = upper - (chromosome[mask] - lower)
    return chromosome


################################################################################


@validate_mutation_dtype
def gaussian_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    gene_rate: float = 0.5,
    strength: float = 0.1,
    gene_bounds: tuple[float, float] = (-1, 1),
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Gaussian Mutation.

    Args:
        chromosome: Chromosome.
        gene_rate: Impact rate on gen.
        strength: Mutation strength.
        gene_bounds: Gene boundaries.

    Returns:
        Mutated chromosome.

    """
    mask = np.random.rand(len(chromosome)) < gene_rate
    noise = np.random.normal(0, strength, mask.sum())
    chromosome[mask] += noise

    lower, upper = gene_bounds
    chromosome = np.clip(chromosome, lower, upper)
    return chromosome


@validate_mutation_dtype
def uniform_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    gene_rate: float = 0.5,
    gene_bounds: tuple[float, float] = (-1, 1),
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Uniform Mutation.

    Args:
        chromosome: Chromosome.
        gene_rate: Impact rate on gen.
        gene_bounds: Gene boundaries.

    Returns:
        Mutated chromosome.

    """
    lower, upper = gene_bounds
    mask = np.random.rand(len(chromosome)) < gene_rate
    chromosome[mask] = np.random.uniform(lower, upper, size=mask.sum())
    return chromosome


################################################################################


def insertion_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Insertion Mutation.

    Args:
        chromosome: Chromosome.

    Returns:
        Mutated chromosome.

    """  # noqa: D401
    source_index = np.random.randint(len(chromosome))
    target_index = np.random.choice(
        np.delete(np.arange(len(chromosome)), source_index)
    )

    gene = chromosome[source_index]
    chromosome = np.delete(chromosome, source_index)
    chromosome = np.insert(chromosome, target_index, gene)
    return chromosome


def inversion_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Inversion Mutation.

    Args:
        chromosome: Chromosome.

    Returns:
        Mutated chromosome.

    """
    chromosome_size = len(chromosome)
    if chromosome_size < 2:
        return chromosome
    start, end = random_segment_indices(chromosome_size)
    chromosome[start:end] = chromosome[start:end][::-1]
    return chromosome


def scramble_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Scramble Mutation.

    Args:
        chromosome: Chromosome.

    Returns:
        Mutated chromosome.

    """
    chromosome_size = len(chromosome)
    if chromosome_size < 2:
        return chromosome
    start, end = random_segment_indices(chromosome_size)
    segment = chromosome[start:end].copy()

    np.random.shuffle(segment)
    chromosome[start:end] = segment
    return chromosome


def shift_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Shift Mutation.

    Args:
        chromosome: Chromosome.

    Returns:
        Mutated chromosome.

    """
    chromosome_size = len(chromosome)
    if chromosome_size < 2:
        return chromosome
    start, end = random_segment_indices(chromosome_size)
    segment = chromosome[start:end].copy()

    shift = np.random.randint(1, len(segment))
    segment = np.roll(segment, shift)
    chromosome[start:end] = segment
    return chromosome


def swap_mutation(
    chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
    """Swap Mutation.

    Args:
        chromosome: Chromosome.

    Returns:
        Mutated chromosome.

    """
    p1, p2 = np.random.choice(len(chromosome), 2, replace=False)
    chromosome[p1], chromosome[p2] = chromosome[p2], chromosome[p1]
    return chromosome
