#!/bin/bash

test_modules="python -m unittest tests.datasetGenerator_test"

[[ "$1" == "watch" ]] && find -name '*.py' | entr $test_modules || $test_modules
