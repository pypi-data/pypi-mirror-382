# galgopy

![PyPI - Status](https://img.shields.io/pypi/status/galgopy)
![PyPI - Version](https://img.shields.io/pypi/v/galgopy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/galgopy)


<p align="center">
<img src="https://raw.githubusercontent.com/vec2pt/galgopy/master/doc/galgopy-00.png" alt="galgopy title image."/>
</p>


A lightweight Python package providing a basic but flexible implementation of the Genetic Algorithm (GA) for optimization tasks.
It can be easily integrated into other projects or extended with custom selection, crossover, and mutation strategies.


## Installation

`galgopy` is available on PyPI:

```bash
pip install galgopy
```

## Usage

### [Sphere Function](https://www.sfu.ca/~ssurjano/spheref.html) Optimization example

```python

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
```

### More examples

More examples can be found in the [examples](https://github.com/vec2pt/galgopy/tree/main/examples) directory.

- [Booth Function Optimization](https://www.sfu.ca/~ssurjano/booth.html)
- [One Max Problem](https://github.com/Oddsor/EvolAlgo/wiki/Max-One-Problem)
- String generation
- [Travelling salesman problem (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem)


## License

This project is licensed under the MIT License.
