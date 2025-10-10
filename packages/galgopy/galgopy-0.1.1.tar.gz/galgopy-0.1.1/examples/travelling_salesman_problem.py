"""Travelling salesman problem (TSP).

Description: https://en.wikipedia.org/wiki/Travelling_salesman_problem
"""

import importlib.util

import numpy as np

from galgopy.crossover import UniformCrossover
from galgopy.ga import GA
from galgopy.mutation import InversionMutation
from galgopy.selection import TournamentSelection
from galgopy.utils import chromosome_to_indices


def plot(points: np.ndarray, solution: np.ndarray) -> None:
    """Plot polygon if matplotlib is installed.

    Args:
        points: Points.
        solution: Solution.

    """
    if importlib.util.find_spec("matplotlib") is None:
        print("'matplotlib' is not installed")
        return
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon

    matplotlib.use("TkAgg")

    _, ax = plt.subplots()
    ax.plot(*points.T, "o")
    polygon = Polygon(
        [points[i] for i in chromosome_to_indices(solution)],
        edgecolor="green",
        facecolor="lightgreen",
    )
    ax.add_patch(polygon)

    ax.set_aspect("equal")
    plt.title("Travelling salesman problem.")
    plt.show()


def fitness_func(chromosome: np.ndarray) -> np.floating:
    """Fitness calculation function for TSP.

    Args:
        chromosome: Chromosome.

    Returns:
        Fitness.

    """
    indices = chromosome_to_indices(chromosome)
    return -np.sum(
        [
            np.linalg.norm(POINTS[indices[i - 1]] - POINTS[g])
            for i, g in enumerate(indices)
        ]
    )


# P01 - Source: https://people.sc.fsu.edu/~jburkardt/datasets/tsp/tsp.html
POINTS = np.array(
    [
        (-0.0000000400893815, 0.0000000358808126),
        (-28.8732862244731230, -0.0000008724121069),
        (-79.2915791686897506, 21.4033307581457670),
        (-14.6577381710829471, 43.3895496964974043),
        (-64.7472605264735108, -21.8981713360336698),
        (-29.0584693142401171, 43.2167287683090606),
        (-72.0785319657452987, -0.1815834632498404),
        (-36.0366489745023770, 21.6135482886620949),
        (-50.4808382862985496, -7.3744722432402208),
        (-50.5859026832315024, 21.5881966132975371),
        (-0.1358203773809326, 28.7292896751977480),
        (-65.0865638413727368, 36.0624693073746769),
        (-21.4983260706612533, -7.3194159498090388),
        (-57.5687244704708050, 43.2505562436354225),
        (-43.0700258454450875, -14.5548396888330487),
    ]
)

ga = GA(
    population_size=100,
    chromosome_size=len(POINTS),
    fitness_func=fitness_func,
    mutation=InversionMutation(individual_rate=0.01),
    crossover=UniformCrossover(),
    selection=TournamentSelection(tournament_size=5),
)

# Init solution and best_fitness
solution, best_fitness = ga.best_chromosome()

for _ in range(1000):
    generation, chromosome, fitness = next(ga)
    if fitness > best_fitness:
        # Update solution and best_fitness
        solution, best_fitness = chromosome, fitness
        print(f"New shortest path found. (Length: {-best_fitness:.4f})")

plot(points=POINTS, solution=solution)
