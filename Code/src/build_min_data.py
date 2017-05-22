#!/usr/bin/env python

import json
from os import path
from datasetGenerator import DatasetGenerator
from concensusFn import least_misery, mean, multiplicative, most_pleasure
import logging
import matplotlib.pyplot as plt
import numpy as np

import sys
import signal

CURRENT_DIR = path.dirname(path.abspath(__file__))
DIR_CACHE_MODELS = path.join(CURRENT_DIR, 'cache')

logging.basicConfig()

logger = logging.getLogger('build_min_data')
logger.setLevel(logging.DEBUG)

# Signal handler
def exit(signum, frame):
    sig_name = tuple(v for v, k in signal.__dict__.items() if k == signum)[0]
    logger.warn('Received signal %s', sig_name)
    sys.exit(0)

for s in [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]:
    signal.signal(s, exit)


CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(CURRENT_DIR, '..', 'data')

dataFilename = path.join(DATA_DIR, 'ratings.csv')

logger.debug("Opening database %s" % dataFilename)
generator = DatasetGenerator(dataFilename, seed=1985)

# Filter dataset. (Remove users with less than 20 ratings)
logger.debug("Filter dataset")
ratings = generator.filterDataset()

# Generating groups of users
group_sizes = [
    (50, 2),
    (18, 3),
    (16, 4),
    (7, 5),
    (5, 6),
    (4, 7)
]
groups = []
for num_groups, size in group_sizes:
    logger.debug("Generating %d groups of %d users", num_groups, size)
    for group, group_type in generator.getGroupUsers(ratings, num_groups, size):
        logger.debug("Group generated: %s -> %d", group_type, len(group))
        groups.append((group, group_type))

# Save groups in cache
logger.debug("Saving groups in cache")
groups_cache_file = path.join(DIR_CACHE_MODELS, 'groups.json')
with open(groups_cache_file, 'w') as f:
    json.dump(groups, f, indent=4)
logger.debug("Groups saved in %s", groups_cache_file)


# Evaluate concensus algorithms
concensus_alg = [{
    "name": "Least misery",
    "fn": least_misery
}, {
    "name": "Mean",
    "fn": mean
}, {
    "name": "Multiplicative",
    "fn": multiplicative
}, {
    "name": "Most pleasure",
    "fn": most_pleasure
}]
for group, group_type in groups:
    for concensus_fn_name, evaluation_success, evaluation_unsuccess in generator.evaluateConcensusFns(ratings, group, concensus_alg):
        # TODO show number of co-rated movies
        logger.debug("Group_size: %d, Group_type: %s, Concensus_alg: %s, Success: %.2f%%, Unsuccess: %.2f%%", size, group_type, concensus_fn_name, evaluation_success, evaluation_unsuccess)

sys.exit(0)

#bins = np.linspace(0, 2500, 100)
#plt.hist(stats_100['countRatingsByUsers'], bins, normed=1, alpha=0.5)
#plt.hist(stats_opt_40['countRatingsByUsers'], bins, normed=1, alpha=0.5)
#plt.hist(stats_opt['countRatingsByUsers'], bins, normed=1, alpha=0.5)
#plt.title("Histogram user ratings")
#plt.show()


# Save it
#rating_min_filename = path.join(DATA_DIR, 'ratings_min.csv')
#logger.debug("Saving file to %s" % rating_min_filename)
#ratings.to_csv(rating_min_filename, index=False)

# Save matrix data
#logger.debug("Generating matrix")
#matrix = generator.getMatrix(ratings)
#matrix_filename = path.join(DATA_DIR, 'matrix.csv')
#logger.debug("Saving matrix file to %s" % matrix_filename)
#matrix.to_csv(matrix_filename)
