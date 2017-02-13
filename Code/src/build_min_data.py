#!/usr/bin/env python

from os import path
from datasetGenerator import DatasetGenerator

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(CURRENT_DIR, '..', 'data')

dataFilename = path.join(DATA_DIR, 'ratings.csv')

generator = DatasetGenerator(dataFilename, seed=1985)

# get sub datasets
ratings_100 = generator.getDataset(percentage=1)
ratings_55 = generator.getDataset(percentage=0.55)
ratings_30 = generator.getDataset(percentage=0.3)

# get optimus dataset 60%
import ipdb; ipdb.set_trace()  # BREAKPOINT
ratings = generator.getOptimusDatasetPercentage(percentage=0.6)

# get optimus dataset
ratings_opt = generator.getOptimusDataset(best_users=1000, best_movies=2000)

# Save it
rating_min_filename = path.join(DATA_DIR, 'ratings_min.csv')
print "Saving file to %s" % rating_min_filename
ratings_opt.to_csv(rating_min_filename, index=False)

# Save matrix data
matrix = generator.getMatrix(ratings_opt)
matrix_filename = path.join(DATA_DIR, 'matrix.csv')
print "Saving matrix file to %s" % matrix_filename
matrix.to_csv(matrix_filename)
