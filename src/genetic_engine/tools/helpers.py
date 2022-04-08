import numpy as np
from deap import creator

INDIVIDUAL_INDEX = 0

def individual_converter(func):
    # fixme: not a must but nice to have, fix if possible.
    """individual must be the first argument and the first return value"""
    def inner(*args, **kwargs):
        individual = args[0]
        if not isinstance(individual, creator.Individual):
            raise KeyError("first argument must be of type creator.Individual!!")

        individual = individual.view(dtype=np.ndarray)
        new_args = []
        new_args[0] = individual
        new_args[1:] = args[1:]
        pass

