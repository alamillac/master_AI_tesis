#!/bin/bash

CURRENT_DIR=$(dirname $0)

source $(which virtualenvwrapper.sh)
workon tesis
${CURRENT_DIR}/../recommender.py
