#!/bin/bash

source $(which virtualenvwrapper.sh)
workon tesis
python -m unittest tests.recommender_test
