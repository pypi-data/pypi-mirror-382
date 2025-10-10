"""Mutation."""

from abc import ABC, abstractmethod

import numpy as np

from .functional import (
    flip_mutation,
    gaussian_mutation,
    insertion_mutation,
    inversion_mutation,
    scramble_mutation,
    shift_mutation,
    swap_mutation,
    uniform_mutation,
)


class AbstractMutation(ABC):
    """Abstract Mutation."""

    def __init__(self, individual_rate: float = 0.01) -> None:
        """Abstract Mutation.

        Args:
            individual_rate: Impact rate.

        """
        super().__init__()
        self._individual_rate = individual_rate

    @abstractmethod
    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """

    def __call__(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation call.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        # Safety copy! (if function works directly on the chromosome)
        chromosome_copy = chromosome.copy()
        if np.random.rand() < self._individual_rate:
            return self.mutation_func(chromosome=chromosome_copy)
        else:
            return chromosome_copy

    def __str__(self) -> str:
        name = self.__class__.__name__
        items_str = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{name}({items_str})"

    def __repr__(self) -> str:
        name = self.__class__.__name__
        items_str = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{name}({items_str})"


################################################################################


class FlipMutation(AbstractMutation):
    """Flip Mutation."""

    def __init__(
        self,
        individual_rate: float = 0.01,
        gene_rate: float = 0.5,
        gene_bounds: tuple[float, float] = (-1, 1),
    ) -> None:
        """Flip Mutation.

        Args:
            individual_rate: Impact rate.
            gene_rate: Impact rate on gen.
            gene_bounds: Gene boundaries.

        """
        super().__init__(individual_rate)
        self._gene_rate = gene_rate
        self._gene_bounds = gene_bounds

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return flip_mutation(
            chromosome=chromosome,
            gene_rate=self._gene_rate,
            gene_bounds=self._gene_bounds,
        )


################################################################################


class GaussianMutation(AbstractMutation):
    """Gaussian Mutation."""

    def __init__(
        self,
        individual_rate: float = 0.01,
        gene_rate: float = 0.5,
        strength: float = 0.1,
        gene_bounds: tuple[float, float] = (-1, 1),
    ) -> None:
        """Gaussian Mutation.

        Args:
            individual_rate: Impact rate.
            gene_rate: Impact rate on gen.
            strength: Mutation strength.
            gene_bounds: Gene boundaries.

        """
        super().__init__(individual_rate)
        self._gene_rate = gene_rate
        self._strength = strength
        self._gene_bounds = gene_bounds

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return gaussian_mutation(
            chromosome=chromosome,
            gene_rate=self._gene_rate,
            strength=self._strength,
            gene_bounds=self._gene_bounds,
        )


class UniformMutation(AbstractMutation):
    """Uniform Mutation."""

    def __init__(
        self,
        individual_rate: float = 0.01,
        gene_rate: float = 0.5,
        gene_bounds: tuple[float, float] = (-1, 1),
    ) -> None:
        """Uniform Mutation.

        Args:
            individual_rate: Impact rate.
            gene_rate: Impact rate on gen.
            gene_bounds: Gene boundaries.

        """
        super().__init__(individual_rate)
        self._gene_rate = gene_rate
        self._gene_bounds = gene_bounds

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return uniform_mutation(
            chromosome=chromosome,
            gene_rate=self._gene_rate,
            gene_bounds=self._gene_bounds,
        )


################################################################################


class InsertionMutation(AbstractMutation):
    """Insertion Mutation."""

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return insertion_mutation(chromosome=chromosome)


class InversionMutation(AbstractMutation):
    """Insertion Mutation."""

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return inversion_mutation(chromosome=chromosome)


class ScrambleMutation(AbstractMutation):
    """Scramble Mutation."""

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return scramble_mutation(chromosome=chromosome)


class ShiftMutation(AbstractMutation):
    """Shift Mutation."""

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return shift_mutation(chromosome=chromosome)


class SwapMutation(AbstractMutation):
    """Swap Mutation."""

    def mutation_func(
        self,
        chromosome: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Mutation function.

        Args:
            chromosome: Chromosome.

        Returns:
            Mutated chromosome.

        """
        return swap_mutation(chromosome=chromosome)
