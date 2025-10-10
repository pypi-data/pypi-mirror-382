"""Sphere Function Optimization.

Description: https://www.sfu.ca/~ssurjano/spheref.html
"""

import numpy as np

from galgopy.crossover import IntermediateRecombination
from galgopy.ga import GA
from galgopy.mutation import UniformMutation
from galgopy.selection import TournamentSelection

ga = GA(
    population_size=100,
    chromosome_size=2,
    gene_bounds=(-5.12, 5.12),
    fitness_func=lambda x: -np.sum(np.square(x)),
    mutation=UniformMutation(individual_rate=0.1, gene_bounds=(-5.12, 5.12)),
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
    "Global minimum:\t[0. 0.]",
    sep="\n",
)
