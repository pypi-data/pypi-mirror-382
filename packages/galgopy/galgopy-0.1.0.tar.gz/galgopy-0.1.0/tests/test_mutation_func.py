import numpy as np
import pytest

import galgopy.mutation.functional as f

REAL_FUNCTIONS = [
    f.flip_mutation,
    f.gaussian_mutation,
    f.uniform_mutation,
]
PERMUTATION_FUNCTIONS = [
    f.insertion_mutation,
    f.inversion_mutation,
    f.scramble_mutation,
    f.shift_mutation,
    f.swap_mutation,
]

REAL_CHROMOSOME = [
    np.random.random(5),
    np.random.uniform(-1, 1, 5),
    np.array([0, 1, 2, 3, 4], dtype=np.float64),
]

NON_REAL_CHROMOSOME = [
    np.random.randint(0, 6, 5),
    np.random.randint(-5, 6, 5),
    np.random.randint(0, 2, 5, dtype=np.bool_),
]


@pytest.mark.parametrize("func", REAL_FUNCTIONS)
@pytest.mark.parametrize("chromosome", REAL_CHROMOSOME)
def test_real(func, chromosome):
    chromosome_copy = chromosome.copy()
    gene_bounds = np.min(chromosome_copy), np.max(chromosome_copy)
    mutated_chromosome = func(chromosome_copy, gene_bounds=gene_bounds)
    assert np.all(mutated_chromosome >= gene_bounds[0])
    assert np.all(mutated_chromosome <= gene_bounds[1])
    assert mutated_chromosome.shape == chromosome_copy.shape
    assert mutated_chromosome.dtype == chromosome_copy.dtype


@pytest.mark.parametrize("func", REAL_FUNCTIONS)
@pytest.mark.parametrize("chromosome", NON_REAL_CHROMOSOME)
def test_real_failed(func, chromosome):
    chromosome_copy = chromosome.copy()
    gene_bounds = np.min(chromosome_copy), np.max(chromosome_copy)
    try:
        func(chromosome_copy, gene_bounds=gene_bounds)
        assert AssertionError
    except ValueError:
        assert True


@pytest.mark.parametrize("func", PERMUTATION_FUNCTIONS)
@pytest.mark.parametrize("chromosome", [*REAL_CHROMOSOME, *NON_REAL_CHROMOSOME])
def test_permutation(func, chromosome):
    chromosome_copy = chromosome.copy()
    mutated_chromosome = func(chromosome_copy)
    assert set(mutated_chromosome) == set(chromosome_copy)
    assert mutated_chromosome.shape == chromosome_copy.shape
    assert mutated_chromosome.dtype == chromosome_copy.dtype
