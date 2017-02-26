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

    def test_similarity(self):
        pass

if __name__ == '__main__':
    unittest.main()
