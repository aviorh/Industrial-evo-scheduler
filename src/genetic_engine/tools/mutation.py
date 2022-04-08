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
    # individual = individual.view(dtype=np.ndarray)

    x, y, z = individual.shape
    for i, j, k in np.ndindex(x, y, z):
        if random.random() < indpb:
            # if theres a product produced at this line at the same time, remove it from schedule
            if individual[i, :, k].any():
                index_of_one = np.where(individual[i, :, k] == 1)[0]
                if index_of_one[0] != j:
                    individual[i, index_of_one, k] = 0
            individual[i, j, k] = type(individual[i, j, k])(not individual[i, j, k])

    # individual = creator.Individual(individual)
    for i, k in np.ndindex(x, z):
        if individual[i,:,k].sum() > 1:
            raise KeyError("shit!!!!")

    return individual,
