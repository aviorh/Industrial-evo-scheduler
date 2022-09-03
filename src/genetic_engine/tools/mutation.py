# Mutations taken from deap.tools.mutation and converted to match np.ndarray format
import random
from deap import creator

import numpy as np


def mutFlipBit(individual, indpb):
    """Flip the value of the attributes of the input individual and return the
    mutant. The *individual* is expected to be a :term:`sequence` and the values of the
    attributes shall stay valid after the ``not`` operator is called on them.
    The *indpb* argument is the probability of each attribute to be
    flipped. This mutation is usually applied on boolean individuals.

    :param individual: Individual to be mutated.
    :param indpb: Independent probability for each attribute to be flipped.
    :returns: A tuple of one individual.

    This function uses the :func:`~random.random` function from the python base
    :mod:`random` module.

    while mutating the solution we also make sure it is still valid.
    """
    x, y, z = individual.shape
    for i, j, k in np.ndindex(x, y, z):
        if random.random() < indpb:
            # if theres a product produced at this line at the same time, remove it from schedule
            if individual[i, :, k].any():
                index_of_one = np.where(individual[i, :, k] == 1)[0]
                if index_of_one[0] != j:
                    individual[i, index_of_one, k] = 0
            individual[i, j, k] = type(individual[i, j, k])(not individual[i, j, k])

    return individual,


def mutShuffleIndexes(individual, indpb):
    """Shuffle the attributes of the input individual and return the mutant.
    The *individual* is expected to be a :term:`sequence`. The *indpb* argument is the
    probability of each attribute to be moved. Usually this mutation is applied on
    vector of indices.

    :param individual: Individual to be mutated.
    :param indpb: Independent probability for each attribute to be exchanged to
                  another position.
    :returns: A tuple of one individual.

    This function uses the :func:`~random.random` and :func:`~random.randint`
    functions from the python base :mod:`random` module.
    """
    num_possible_shuffles = round(individual.size / 2)
    shape = individual.shape
    for i in range(num_possible_shuffles):
        if random.random() < indpb:
            swap_idx_a = (random.randint(0, shape[0] - 1), random.randint(0, shape[1] - 1), random.randint(0, shape[2] - 1))
            swap_idx_b = (random.randint(0, shape[0] - 1), random.randint(0, shape[1] - 1), random.randint(0, shape[2] - 1))
            if swap_idx_a != swap_idx_b:
                individual[swap_idx_a], individual[swap_idx_b] = individual[swap_idx_b], individual[swap_idx_a]

    return individual,