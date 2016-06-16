#!/usr/bin/env python

from pandas import read_csv, DataFrame
import numpy as np
from os import path

CURRENT_DIR = path.dirname(path.abspath(__file__))
DATA_DIR = path.join(CURRENT_DIR, '..', 'data')


class Recommender(object):
    def __init__(self, matrixFilename):
        # Read Data file
        print "Reading file: %s" % matrixFilename
        self.matrix = read_csv(matrixFilename, index_col=0, header=0)
        #import ipdb; ipdb.set_trace()  # BREAKPOINT  # TODO Revisar si el indexado es correcto self.matrix.loc[5,'768']


if __name__ == '__main__':
    dataFilename = path.join(DATA_DIR, 'matrix.csv')
    recommender = Recommender(dataFilename)
