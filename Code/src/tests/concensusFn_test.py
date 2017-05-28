#!/usr/bin/env python

import unittest
from os import path
from datasetGenerator import DatasetGenerator
from concensusFn import least_misery, mean, multiplicative, most_pleasure, borda_count, purity
from pandas import Series
from numpy import array_equal

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_TEST_DIR = path.join(CURRENT_DIR, 'data_test')


class TestConcensusFn(unittest.TestCase):
    def setUp(self):
        dataFilename = path.join(DATA_TEST_DIR, 'concensus_ratings_test.csv')
        generator = DatasetGenerator(dataFilename)
        ratings = generator.getDatasetPercentage(percentage=1)
        self.matrix = generator.getMatrix(ratings)

    def test_least_misery(self):
        expected = Series([4, 4, 2, 6, 6, 6, 5, 6, 3, 6], index=self.matrix.keys())
        model = least_misery(self.matrix)
        self.assertTrue(array_equal(model, expected))

    def test_mean(self):
        expected = Series([7.75, 6, 5.5, 7.5, 8, 7.75, 6.75, 8, 7.25, 7.75], index=self.matrix.keys())
        model = mean(self.matrix)
        self.assertTrue(array_equal(model, expected))

    def test_multiplicative(self):
        expected = Series([2800, 1080, 432, 3024, 3780, 3402, 1800, 3888, 1890, 3456], index=self.matrix.keys())
        model = multiplicative(self.matrix)
        self.assertTrue(array_equal(model, expected))

    def test_most_pleasure(self):
        expected = Series([10, 9, 9, 9, 10, 9, 10, 9, 10, 9], index=self.matrix.keys())
        model = most_pleasure(self.matrix)
        self.assertTrue(array_equal(model, expected))

    def test_borda_count(self):
        expected = Series([25, 15, 15, 24, 24, 24.5, 19, 26, 24.5, 23], index=self.matrix.keys())
        model = borda_count(self.matrix)
        self.assertTrue(array_equal(model, expected))

    def test_purity(self):
        expected = Series([0.759, 0.588, 0.531, 0.743, 0.790, 0.767, 0.663, 0.792, 0.708, 0.768], index=self.matrix.keys())
        model = purity(self.matrix)
        self.assertTrue(array_equal(model, expected))



if __name__ == '__main__':
    unittest.main()
