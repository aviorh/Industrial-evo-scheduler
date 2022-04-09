import random

import numpy as np


def cxTwoPoint(ind1, ind2):
    """Executes a two-point crossover on the input :term:`sequence`
    individuals. The two individuals are modified in place and both keep
    their original length.

    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :returns: A tuple of two individuals.

    This function uses the :func:`~random.randint` function from the Python
    base :mod:`random` module.

    we swap a 3D box-shaped area in both individuals
    """
    cxpoint1_x, cxpoint2_x = _get_cx_points(min(ind1.shape[0], ind2.shape[0]))
    cxpoint1_z, cxpoint2_z = _get_cx_points(min(ind1.shape[2], ind2.shape[2]))

    ind1[cxpoint1_x:cxpoint2_x, :, cxpoint1_z:cxpoint2_z], \
    ind2[cxpoint1_x:cxpoint2_x, :, cxpoint1_z:cxpoint2_z] \
        = ind2[cxpoint1_x:cxpoint2_x, :, cxpoint1_z:cxpoint2_z].copy(), \
          ind1[cxpoint1_x:cxpoint2_x, :, cxpoint1_z:cxpoint2_z].copy()

    return ind1, ind2


def _get_cx_points(size):
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1
    return cxpoint1, cxpoint2
