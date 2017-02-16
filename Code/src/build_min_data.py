#!/usr/bin/env python

from os import path
from datasetGenerator import DatasetGenerator
import logging

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
logger.debug(stats_100)
logger.debug("Generating dataset 55%")
ratings_55 = generator.getDataset(percentage=0.55)
logger.debug("Generating dataset 30%")
ratings_30 = generator.getDataset(percentage=0.3)

# get optimus dataset 60%
logger.debug("Generating optimus dataset 60%")
ratings = generator.getOptimusDatasetPercentage(percentage=0.6)

# get optimus dataset
num_users = 1000
num_movies = 2000
logger.debug("Generating optimus dataset users=%d, movies=%d" % (num_users, num_movies))
ratings_opt = generator.getOptimusDataset(best_users=num_users, best_movies=num_movies)

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
