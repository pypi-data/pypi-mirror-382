"""Booth Function Optimization.

Description: https://www.sfu.ca/~ssurjano/booth.html
"""

import numpy as np

from galgopy.crossover import IntermediateRecombination
from galgopy.ga import GA
from galgopy.mutation import UniformMutation
from galgopy.selection import TournamentSelection


# Definition of fitness function.
def booth_func(chromosome: np.ndarray) -> float:
    """Booth Function."""
    x, y = chromosome
    fitness = (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2
    # To minimize: return -fitness
    return -fitness


ga = GA(
    population_size=100,
    chromosome_size=2,
    gene_bounds=(-10, 10),
    fitness_func=booth_func,
    mutation=UniformMutation(individual_rate=0.1, gene_bounds=(-10, 10)),
    crossover=IntermediateRecombination(),
    selection=TournamentSelection(),
)

# The course of 50 generations.
for _ in range(50):
    next(ga)

# Result
best_chromosome, _ = ga.best_chromosome()
print(
    f"Result:\t{best_chromosome}",
    "Global minimum:\t[1. 3.]",
    sep="\n",
)
