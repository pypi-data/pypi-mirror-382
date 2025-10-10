"""Selection."""

from abc import ABC, abstractmethod

import numpy as np

from .functional import (
    elitist_selection,
    fitness_proportionate_selection,
    random_selection,
    rank_based_selection,
    stochastic_universal_sampling,
    tournament_selection,
)


class AbstractSelection(ABC):
    """Abstract Selection."""

    def __init__(self, parents_count: int = 2) -> None:
        """Abstract Selection.

        Args:
            parents_count: Number of parents to select.

        """
        super().__init__()
        self._parents_count = parents_count

    @abstractmethod
    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401

    def __call__(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection call.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return self.selection_func(population=population, fitness=fitness)

    def __str__(self) -> str:
        name = self.__class__.__name__
        items_str = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{name}({items_str})"

    def __repr__(self) -> str:
        name = self.__class__.__name__
        items_str = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{name}({items_str})"


class ElitistSelection(AbstractSelection):
    """Elitist Selection."""

    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return elitist_selection(
            population=population,
            fitness=fitness,
            parents_count=self._parents_count,
        )


class FitnessProportionateSelection(AbstractSelection):
    """Fitness Proportionate Selection (FPS) / Roulette Wheel Selection."""

    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return fitness_proportionate_selection(
            population=population,
            fitness=fitness,
            parents_count=self._parents_count,
        )


class RandomSelection(AbstractSelection):
    """Random Selection."""

    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return random_selection(
            population=population,
            fitness=fitness,
            parents_count=self._parents_count,
        )


class RankBasedSelection(AbstractSelection):
    """Rank-Based Selection."""

    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return rank_based_selection(
            population=population,
            fitness=fitness,
            parents_count=self._parents_count,
        )


class StochasticUniversalSampling(AbstractSelection):
    """Stochastic Universal Sampling (SUS)."""

    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return stochastic_universal_sampling(
            population=population,
            fitness=fitness,
            parents_count=self._parents_count,
        )


class TournamentSelection(AbstractSelection):
    """Tournament Selection."""

    def __init__(
        self, parents_count: int = 2, tournament_size: int = 3
    ) -> None:
        """Tournament Selection.

        Args:
            parents_count: Number of parents to select.
            tournament_size: Number of participants in the tournament.

        """
        super().__init__()
        self._parents_count = parents_count
        self._tournament_size = tournament_size

    def selection_func(
        self,
        population: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        fitness: np.ndarray[tuple[int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Selection function.

        Args:
            population: Population.
            fitness: Fitness.

        Returns:
            Selected parents.

        """  # noqa: D401
        return tournament_selection(
            population=population,
            fitness=fitness,
            parents_count=self._parents_count,
            tournament_size=self._tournament_size,
        )
