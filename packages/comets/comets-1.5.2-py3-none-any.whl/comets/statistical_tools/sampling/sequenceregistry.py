# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.
import inspect
import numpy
import scipy.stats

from ...utilities.registry import Registry


SequenceRegistry = Registry()

# Random rule in unit hypercube, using scipy stats.uniform on multiple dimensions
uniform_sampler = scipy.stats.uniform(loc=0, scale=1)


def random(number_of_samples, dim=1, random_state=None):
    return uniform_sampler.rvs((dim, number_of_samples), random_state=random_state)


# LHS sampling methods
def latin_hypercube(number_of_samples, dim=1, random_state=None):
    sampler = scipy.stats.qmc.LatinHypercube(d=dim, seed=random_state)
    return sampler.random(n=number_of_samples).T


def centered_latin_hypercube(number_of_samples, dim=1, random_state=None):
    # 'scrambling' option was added in version 1.10
    # 'centered' will be remove in version 1.12
    sampler = scipy.stats.qmc.LatinHypercube(d=dim, seed=random_state, scramble=False)
    return sampler.random(n=number_of_samples).T


# Sobol sequences
def sobol(number_of_samples, dim=1, random_state=None):
    sampler = scipy.stats.qmc.Sobol(d=dim, scramble=True, seed=random_state)
    return sampler.random(n=number_of_samples).T


# Halton sequences
def halton(number_of_samples, dim=1, random_state=None, scramble=True):
    sampler = scipy.stats.qmc.Halton(d=dim, scramble=scramble, seed=random_state)
    return sampler.random(n=number_of_samples).T


def hammersley(number_of_samples, dim=1, random_state=None, scramble=True):
    # Hammersley sequence is a Halton sequence with one additional dimension being a simple parameter sweep
    if dim == 1:
        return halton(number_of_samples, dim=1, random_state=None, scramble=scramble)
    else:
        samples = numpy.empty((dim, number_of_samples), dtype=float)
        sampler = scipy.stats.qmc.Halton(
            d=dim - 1, scramble=scramble, seed=random_state
        )
        samples[: dim - 1, :] = sampler.random(n=number_of_samples).T
        samples[dim - 1, :] = numpy.linspace(0, 1, number_of_samples + 2)[1:-1]
        return samples


# Register random sampler using scipy stats.uniform
SequenceRegistry.register(random, name="random", info={"HasIterations": True})

# Register other scipy.stats sequences
scipy_sequences = {
    'latin_hypercube': latin_hypercube,
    'centered_latin_hypercube': centered_latin_hypercube,
    'sobol': sobol,
    'halton': halton,
    'hammersley': hammersley,
}


for name, func in scipy_sequences.items():
    params = {"HasIterations": False}
    SequenceRegistry.register(func, name=name, info=params)
