#!/usr/bin/env python

from os import path
import unittest
from datasetGenerator import DatasetGenerator
from numpy import nan
from numpy.testing import assert_equal

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_TEST_DIR = path.join(CURRENT_DIR, 'data_test')


class TestDatasetGenerator(unittest.TestCase):
    def setUp(self):
        dataFilename = path.join(DATA_TEST_DIR, 'ratings_test.csv')
        self.generator = DatasetGenerator(dataFilename, seed=1985)
        #ratings = generator.getDatasetPercentage(percentage=1)
        #matrix = generator.getMatrix(ratings)
        #distances = generator.getDistances(ratings, 58340)
        #sim_users, rem_raitings = generator.getMostSimilarUsers(ratings, 58340, 3)
        #sim_users, rem_raitings = generator.getMostSimilarUsers(ratings, 196761, 3)
        #groups = generator.getGroupUsers(ratings, [3, 4, 6])

    def test_getDistances(self):
        ratings = self.generator.getDatasetPercentage(percentage=1)
        distances = self.generator.getDistances(ratings, 55587)
        expected_distances = {
            #userID: distance
            55587: 0,
            58340: 1.5*8/2,
            91363: 6.0*8/4,
            95577: 8.0*8/6,
            121870: nan,
            127180: 14.0*8/8,
            151659: 2.0*8/1,
            155465: 9.0*8/6,
            196761: 9.0*8/6,
            200012: 2.0*8/1
        }

        for user_id in distances.index:
            assert_equal(distances[user_id], expected_distances[user_id])


if __name__ == '__main__':
    unittest.main()
