#!/usr/bin/env python

from os import path
from datasetGenerator import DatasetGenerator
import logging
import matplotlib.pyplot as plt
import numpy as np

import sys

logging.basicConfig()

logger = logging.getLogger('build_min_data')
logger.setLevel(logging.DEBUG)

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
for num_groups, size in group_sizes:
    logger.debug("Generating %d groups of %d users", num_groups, size)
    groups = generator.getGroupUsers(ratings, num_groups, size)
    logger.debug(groups)

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
