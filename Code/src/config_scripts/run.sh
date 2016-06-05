#!/bin/bash

CURRENT_DIR=$(dirname $0)

source $(which virtualenvwrapper.sh)
workon tesis
${CURRENT_DIR}/../build_min_data.py
