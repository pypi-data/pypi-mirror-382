"""Set of crossover functions."""

import numpy as np

from galgopy.utils import pick_two_parents, validate_crossover_dtype


def one_point_crossover(
    parents: np.ndarray[tuple[int, int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """One-point Crossover.

    Args:
        parents: Parants.

    Returns:
        Children.

    """
    _, chromosome_size = parents.shape

    # TODO: This is definitely not the best method.
    parent1, parent2 = pick_two_parents(parents)

    # Classic implementation for two parents.
    point = np.random.randint(1, chromosome_size)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return np.array([child1, child2])


def multi_point_crossover(
    parents: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    points_count: int = 2,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Multi-Point Crossover / k-point Crossover.

    Args:
        parents: Parants.
        points_count: Number of split points.

    Returns:
        Children.

    """
    _, chromosome_size = parents.shape

    # TODO: This is definitely not the best method.
    parent1, parent2 = pick_two_parents(parents)

    points = np.sort(
        np.random.choice(
            np.arange(1, chromosome_size),
            size=points_count,
            replace=False,
        )
    )
    points = np.concatenate([[0], points, [chromosome_size]])
    child1, child2 = parent1.copy(), parent2.copy()
    for i in range(points_count + 1):
        start, end = points[i], points[i + 1]
        if i % 2 != 0:
            child1[start:end] = parent2[start:end]
            child2[start:end] = parent1[start:end]
    return np.array([child1, child2])


def uniform_crossover(
    parents: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    gene_rate: float = 0.5,
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Uniform Crossover.

    Args:
        parents: Parants.
        gene_rate: Impact rate on gen.

    Returns:
        Children.

    """
    _, chromosome_size = parents.shape

    # TODO: This is definitely not the best method.
    parent1, parent2 = pick_two_parents(parents)

    mask = np.random.rand(chromosome_size) < gene_rate
    child1 = np.where(mask, parent1, parent2)
    child2 = np.where(mask, parent2, parent1)
    return np.array([child1, child2])


@validate_crossover_dtype
def whole_arithmetic_recombination(
    parents: np.ndarray[tuple[int, int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Whole arithmetic recombination.

    Args:
        parents: Parants.

    Returns:
        Children.

    """
    parents_count = len(parents)
    if parents_count == 2:
        # Classic implementation for two parents.
        parent1, parent2 = parents
        alpha = np.random.rand()

        child1 = alpha * parent1 + (1 - alpha) * parent2
        child2 = (1 - alpha) * parent1 + alpha * parent2
        # Works faster than: np.stack([child1, child2])
        return np.array([child1, child2])
    else:
        alphas = np.ones(parents_count) / parents_count
        child = np.sum(parents * alphas[:, None], axis=0)
        # Works faster than: np.expand_dims(child, axis=0)
        return np.array([child])


@validate_crossover_dtype
def intermediate_recombination(
    parents: np.ndarray[tuple[int, int], np.dtype[np.float64]],
) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
    """Intermediate recombination.

    Args:
        parents: Parants.

    Returns:
        Children.

    """
    parents_count, chromosome_size = parents.shape
    if parents_count == 2:
        # Classic implementation for two parents.
        parent1, parent2 = parents
        alpha = np.random.rand(chromosome_size)

        child1 = alpha * parent1 + (1 - alpha) * parent2
        child2 = alpha * parent2 + (1 - alpha) * parent1
        return np.array([child1, child2])
    else:
        alphas = np.random.dirichlet(
            np.ones(parents_count), size=chromosome_size
        ).T
        child = np.sum(parents * alphas, axis=0)
        return np.array([child])
