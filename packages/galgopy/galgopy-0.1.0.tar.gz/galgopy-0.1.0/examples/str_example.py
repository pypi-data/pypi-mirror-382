"""An example of string generation.

Inspired by 'Example 9.1: Genetic Algorithm for Evolving Shakespeare' from
Daniel Shiffman's book 'The Nature of Code'.

Link:
'Example 9.1: Genetic Algorithm for Evolving Shakespeare': https://natureofcode.com/genetic-algorithms/#example-91-genetic-algorithm-for-evolving-shakespeare
"""

import numpy as np

from galgopy.crossover import UniformCrossover
from galgopy.ga import GA
from galgopy.mutation import AbstractMutation
from galgopy.mutation.functional import swap_mutation, uniform_mutation
from galgopy.selection import TournamentSelection
from galgopy.utils import chromosome_to_int


def fitness_func(chromosome: np.ndarray) -> float:
    """Fitness function."""
    data = chromosome_to_int(chromosome, int_bounds=(32, 127))
    out = np.sum([chr(g) == c for g, c in zip(data, list(STR), strict=True)])
    return out.astype(np.float64)


def print_stat(ga: GA) -> None:
    """Print stat."""

    def chromosome_to_str(chromosome: np.ndarray) -> str:
        data = chromosome_to_int(chromosome, int_bounds=(32, 127))
        return "".join([chr(g) for g in data])

    generation = ga.generation
    chromosome, fitness = ga.best_chromosome()
    print(
        f"Generation: {generation}.",
        f"Result: '{chromosome_to_str(chromosome)}'",
        f"Fitness: {fitness:.4f}",
        sep="\t",
    )


# Example of a custom mutation. 25% Uniform / 75% Swap
class CustomMutation(AbstractMutation):
    """Custom Mutation."""

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
        if np.random.random() > 0.25:
            return swap_mutation(chromosome=chromosome)
        else:
            return uniform_mutation(chromosome=chromosome)


STR = "To be, or not to be"

population_size = 300
chromosome_size = len(STR)
crossover = UniformCrossover()
selection = TournamentSelection(tournament_size=5)
mutation = CustomMutation(individual_rate=1 / chromosome_size)

expected_fitness = len(STR)
generations = 200

ga = GA(
    population_size=population_size,
    chromosome_size=chromosome_size,
    fitness_func=fitness_func,
    mutation=mutation,
    crossover=crossover,
    selection=selection,
)

# Replaces the first population with a larger one.
ga.population = np.random.uniform(-1, 1, (500, chromosome_size))

print_stat(ga)
for generation, _, fitness in ga:
    print_stat(ga)
    if generation == generations or fitness == expected_fitness:
        break
