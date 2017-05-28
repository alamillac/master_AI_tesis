import numpy as np

def least_misery(group_matrix):
    return group_matrix.apply(min)

def mean(group_matrix):
    return group_matrix.apply(np.mean)

def purity(group_matrix):
    std_array = group_matrix.apply(np.std)
    # TODO Not working
    return (group_matrix-std_array).apply(sum) / group_matrix.apply(sum)

def multiplicative(group_matrix):
    def multiply(array):
        return reduce(lambda x, y: x*y, array)
    return group_matrix.apply(multiply)

def most_pleasure(group_matrix):
    return group_matrix.apply(max)

def borda_count(group_matrix):
    ranks = group_matrix.copy()
    for index, row in group_matrix.iterrows():
        i = 0
        for rank, count_rank in row.value_counts().sort_index().iteritems():
            new_rank = np.mean(range(i+1, i+count_rank+1))
            i += count_rank
            ranks.loc[index].replace(to_replace=rank, value=new_rank, inplace=True)
    return ranks.apply(sum)
