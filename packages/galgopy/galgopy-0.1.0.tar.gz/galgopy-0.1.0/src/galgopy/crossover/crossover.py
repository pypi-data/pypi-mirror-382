"""Crossover."""

from abc import ABC, abstractmethod

import numpy as np

from .functional import (
    intermediate_recombination,
    multi_point_crossover,
    one_point_crossover,
    uniform_crossover,
    whole_arithmetic_recombination,
)


class AbstractCrossover(ABC):
    """Abstract Crossover."""

    def __init__(self, rate: float = 0.9) -> None:
        """Abstract Crossover.

        Args:
            rate: Impact rate.

        """
        super().__init__()
        self._rate = rate

    @abstractmethod
    def crossover_func(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover function.

        Args:
            parents: Parants.

        Returns:
            Children.

        """

    def __call__(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover call.

        Args:
            parents: Parants.

        Returns:
            Children.

        """
        if len(parents) <= 1:
            # Skip the 'crossover' for one parent.
            # In this case, only mutation is used.
            return parents
        else:
            # Safety copy! (if function works directly on the chromosome)
            parents_copy = parents.copy()
            if np.random.rand() < self._rate:
                return self.crossover_func(parents=parents_copy)
            else:
                return parents_copy

    def __str__(self) -> str:
        name = self.__class__.__name__
        items_str = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{name}({items_str})"

    def __repr__(self) -> str:
        name = self.__class__.__name__
        items_str = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{name}({items_str})"


class OnePointCrossover(AbstractCrossover):
    """One-point Crossover."""

    def crossover_func(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover function.

        Args:
            parents: Parants.

        Returns:
            Children.

        """
        return one_point_crossover(parents=parents)


class MultipointCrossover(AbstractCrossover):
    """Multi-Point Crossover / k-point Crossover."""

    def __init__(self, rate: float = 0.9, points_count: int = 2) -> None:
        """Multi-Point Crossover / k-point Crossover.

        Args:
            rate: Impact rate.
            points_count: Number of split points.

        """
        super().__init__(rate)
        self._points_count = points_count

    def crossover_func(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover function.

        Args:
            parents: Parants.

        Returns:
            Children.

        """
        return multi_point_crossover(
            parents=parents, points_count=self._points_count
        )


class UniformCrossover(AbstractCrossover):
    """Uniform Crossover."""

    def __init__(self, rate: float = 0.9, gene_rate: float = 0.5) -> None:
        """Uniform Crossover.

        Args:
            rate: Impact rate.
            gene_rate: Impact rate on gen.

        """
        super().__init__(rate)
        self._gene_rate = gene_rate

    def crossover_func(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover function.

        Args:
            parents: Parants.

        Returns:
            Children.

        """
        return uniform_crossover(parents=parents, gene_rate=self._gene_rate)


class WholeArithmeticRecombination(AbstractCrossover):
    """Whole arithmetic recombination."""

    def crossover_func(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover function.

        Args:
            parents: Parants.

        Returns:
            Children.

        """
        return whole_arithmetic_recombination(parents=parents)


class IntermediateRecombination(AbstractCrossover):
    """Intermediate recombination."""

    def crossover_func(
        self, parents: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Crossover function.

        Args:
            parents: Parants.

        Returns:
            Children.

        """
        return intermediate_recombination(parents=parents)
