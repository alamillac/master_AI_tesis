import numpy as np

def least_misery(group_matrix):
    return group_matrix.apply(min)

def mean(group_matrix):
    return group_matrix.apply(np.mean)

def multiplicative(group_matrix):
    def multiply(array):
        return reduce(lambda x, y: x*y, array)
    return group_matrix.apply(multiply)

def most_pleasure(group_matrix):
    return group_matrix.apply(max)

def borda_count(group_matrix):
    import ipdb; ipdb.set_trace()  # BREAKPOINT
    #set(group_matrix.loc['Anne'])
    #group_matrix.loc['Anne'].sort_values()
    #len([rate for rate in group_matrix.loc['Anne'] if rate == 8.0])
    return []
