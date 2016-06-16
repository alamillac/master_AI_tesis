#!/usr/bin/env python

from os import path
from recommender import Recommender
import unittest

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_TEST_DIR = path.join(CURRENT_DIR, 'data_test')


class TestRecommender(unittest.TestCase):
    def setUp(self):
        dataFilename = path.join(DATA_TEST_DIR, 'matrix_test.csv')
        self.recommender = Recommender(dataFilename)
        print self.recommender.matrix

    def test_similarity(self):
        pass

if __name__ == '__main__':
    unittest.main()
