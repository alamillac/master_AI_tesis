#!/usr/bin/env python

from os import path
import unittest
from datasetGenerator import DatasetGenerator

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_TEST_DIR = path.join(CURRENT_DIR, 'data_test')


class TestDatasetGenerator(unittest.TestCase):
    def setUp(self):
        dataFilename = path.join(DATA_TEST_DIR, 'ratings_test.csv')
        generator = DatasetGenerator(dataFilename, seed=1985)
        ratings = generator.getDatasetPercentage(percentage=1)
        matrix = generator.getMatrix(ratings)
        distances = generator.getDistances(ratings, 58340)
        sim_users, rem_raitings = generator.getMostSimilarUsers(ratings, 58340, 3)
        sim_users, rem_raitings = generator.getMostSimilarUsers(ratings, 196761, 3)
        groups = generator.getGroupUsers(ratings, [3, 4, 6])
        import ipdb; ipdb.set_trace()  # BREAKPOINT

    def test_similarity(self):
        pass

if __name__ == '__main__':
    unittest.main()
