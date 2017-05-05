import numpy as np

def least_misery(group_matrix):
    return group_matrix.apply(min)

def mean(group_matrix):
    return group_matrix.apply(np.mean)
