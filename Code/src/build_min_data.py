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

# get sub datasets
logger.debug("Generating dataset 100%")
ratings_100 = generator.getDataset(percentage=1)
logger.debug("Stats from dataset 100%")
stats_100 = generator.getStatsFromDataset(ratings_100)

#plt.hist(stats_100['countRatingsByUsers'])
logger.debug("Generating dataset 55%")
ratings_55 = generator.getDataset(percentage=0.55)

logger.debug("Generating dataset 30%")
ratings_30 = generator.getDataset(percentage=0.3)
stats_30 = generator.getStatsFromDataset(ratings_30)

# get optimus dataset 40%
logger.debug("Generating optimus dataset 40%")
ratings_opt_40 = generator.getOptimusDatasetPercentage(percentage=0.4)
logger.debug("Stats from dataset optimus 40%")
stats_opt_40 = generator.getStatsFromDataset(ratings_opt_40)

# get optimus dataset
num_users = 1000
num_movies = 2000
logger.debug("Generating optimus dataset users=%d, movies=%d" % (num_users, num_movies))
ratings_opt = generator.getOptimusDataset(best_users=num_users, best_movies=num_movies)
logger.debug("Stats from dataset optimus")
stats_opt = generator.getStatsFromDataset(ratings_opt)

bins = np.linspace(0, 2500, 100)
plt.hist(stats_100['countRatingsByUsers'], bins, normed=1, alpha=0.5)
plt.hist(stats_30['countRatingsByUsers'], bins, normed=1, alpha=0.5)
plt.hist(stats_opt_40['countRatingsByUsers'], bins, normed=1, alpha=0.5)
plt.hist(stats_opt['countRatingsByUsers'], bins, normed=1, alpha=0.5)
plt.title("Histogram user ratings")
plt.show()

sys.exit(0)

# Save it
rating_min_filename = path.join(DATA_DIR, 'ratings_min.csv')
logger.debug("Saving file to %s" % rating_min_filename)
ratings_opt.to_csv(rating_min_filename, index=False)

# Save matrix data
logger.debug("Generating matrix")
matrix = generator.getMatrix(ratings_opt)
matrix_filename = path.join(DATA_DIR, 'matrix.csv')
logger.debug("Saving matrix file to %s" % matrix_filename)
matrix.to_csv(matrix_filename)
