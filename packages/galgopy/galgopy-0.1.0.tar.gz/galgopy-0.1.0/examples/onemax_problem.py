"""One Max Problem.

Description: https://github.com/Oddsor/EvolAlgo/wiki/Max-One-Proble
"""

import numpy as np

from galgopy.crossover import UniformCrossover
from galgopy.ga import GA
from galgopy.mutation import FlipMutation
from galgopy.selection import TournamentSelection
from galgopy.utils import chromosome_to_bool


# Definition of fitness function.
def onemax_func(x: np.ndarray) -> float:
    """One Max fitness calculation."""
    return np.sum(chromosome_to_bool(x).astype(np.float64))


# Helper function for plotting stat.
def print_stat(generations: int, ga: GA) -> None:
    """Print stat."""
    _, best_fitness = ga.best_chromosome()
    _, worst_fitness = ga.worst_chromosome()
    print(
        f"[{ga.generation}/{generations}]",
        f"Max_fitness: {best_fitness:.0f}",
        f"Min_fitness: {worst_fitness:.0f}",
        f"Avg_fitness: {ga.average_fitness()}",
        f"Std: {np.std(ga.fitness):.4f}",
        sep="\t",
    )


# GA settings
population_size = 100
chromosome_size = 20
selection = TournamentSelection(parents_count=2, tournament_size=3)
crossover = UniformCrossover()
mutation = FlipMutation(individual_rate=1 / chromosome_size)

# Termination settings
expected_fitness = chromosome_size
generations = 20

ga = GA(
    population_size=population_size,
    chromosome_size=chromosome_size,
    fitness_func=onemax_func,
    selection=selection,
    crossover=crossover,
    mutation=mutation,
)

# Output init stats
print_stat(generations, ga)

for generation, _, best_fitness in ga:
    # Output evolution stats
    print_stat(generations, ga)

    # Termination
    if generation == generations or best_fitness == expected_fitness:
        break
