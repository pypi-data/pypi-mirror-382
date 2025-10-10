"""Genetic algorithm."""

from collections.abc import Callable
from typing import Self

import numpy as np


class GA:
    """Genetic algorithm."""

    def __init__(
        self,
        population_size: int,
        chromosome_size: int,
        fitness_func: Callable[
            [np.ndarray[tuple[int], np.dtype[np.float64]]], np.floating | float
        ],
        mutation: Callable[
            [np.ndarray[tuple[int], np.dtype[np.float64]]],
            np.ndarray[tuple[int], np.dtype[np.float64]],
        ],
        crossover: Callable[
            [np.ndarray[tuple[int, int], np.dtype[np.float64]]],
            np.ndarray[tuple[int, int], np.dtype[np.float64]],
        ],
        selection: Callable[
            [
                np.ndarray[tuple[int, int], np.dtype[np.float64]],
                np.ndarray[tuple[int], np.dtype[np.float64]],
            ],
            np.ndarray[tuple[int, int], np.dtype[np.float64]],
        ],
        gene_bounds: tuple[float, float] = (-1, 1),
    ) -> None:
        """Genetic algorithm.

        Args:
            population_size: Population size.
            chromosome_size: Chromosome size.
            fitness_func: Fitness function.
            mutation: Mutation.
            crossover: Crossover.
            selection: Selection.
            gene_bounds: Gene boundaries.

        """
        self._population_size = population_size
        self._chromosome_size = chromosome_size
        self._gene_bounds = gene_bounds
        self._fitness_func = fitness_func
        self._mutation = mutation
        self._crossover = crossover
        self._selection = selection
        self.generation = 0
        self._population = self._init_population()
        self.fitness = self._evaluate(self._population)

    @property
    def population(self) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Population.

        Returns:
            Population

        """
        return self._population

    @population.setter
    def population(
        self, new_population: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> None:
        # TODO: Add verification
        self._population = new_population
        self.fitness = self._evaluate(self._population)

    def _init_population(
        self,
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        lower, upper = self._gene_bounds
        return np.random.uniform(
            lower, upper, size=(self._population_size, self._chromosome_size)
        )

    def _evaluate(
        self, population: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        fitness = np.apply_along_axis(self._fitness_func, 1, population)
        return fitness

    def _create_next_population(
        self,
    ) -> np.ndarray[tuple[int, int], np.dtype[np.float64]]:
        # Apply selection and crossover
        new_population = []
        while len(new_population) < self._population_size:
            parents = self._selection(self._population, self.fitness)
            children = self._crossover(parents)
            new_population.extend(children)
        # Fit the new population to the required size
        new_population = np.array(new_population[: self._population_size])

        # Apply mutation
        new_population = np.apply_along_axis(self._mutation, 1, new_population)
        return new_population

    def best_chromosome(
        self,
    ) -> tuple[np.ndarray[tuple[int], np.dtype[np.float64]], float]:
        """Best chromosome.

        Returns:
            Best chromosome and its fitness.

        """
        best_index = np.argmax(self.fitness)
        return self._population[best_index], self.fitness[best_index]

    def worst_chromosome(
        self,
    ) -> tuple[np.ndarray[tuple[int], np.dtype[np.float64]], float]:
        """Worst chromosome.

        Returns:
            Worst chromosome and its fitness.

        """
        worst_index = np.argmin(self.fitness)
        return self._population[worst_index], self.fitness[worst_index]

    def average_fitness(self) -> float:
        """Average fitness.

        Returns:
            Average fitness.

        """
        return np.mean(self.fitness).astype(float)

    def __iter__(self) -> Self:
        return self

    def __next__(
        self,
    ) -> tuple[int, np.ndarray[tuple[int], np.dtype[np.float64]], float]:
        self._population = self._create_next_population()
        self.fitness = self._evaluate(self._population)
        self.generation += 1
        best_chromosome, best_fitness = self.best_chromosome()
        return self.generation, best_chromosome, best_fitness

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(generation={self.generation})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(generation={self.generation})"
