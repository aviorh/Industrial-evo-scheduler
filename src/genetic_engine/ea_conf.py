from deap import base
from deap import creator
from deap import tools

import random
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

# problem constants:
SOFT_CONSTRAINT_PENALTY = 1
HARD_CONSTRAINT_PENALTY = 10  # the penalty factor for a hard-constraint violation
INVALID_SCHEDULING_PENALTY = 100

# Genetic Algorithm constants:
POPULATION_SIZE = 300
P_CROSSOVER = 0.9  # probability for crossover
P_MUTATION = 0.1   # probability for mutating an individual
MAX_GENERATIONS = 20
HALL_OF_FAME_SIZE = 30

# set the random seed:
RANDOM_SEED = 42
