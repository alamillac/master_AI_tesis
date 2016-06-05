#!/bin/bash

color=`tput setaf 1`
reset=`tput sgr0`

if ! which virtualenvwrapper.sh &>/dev/null ; then
    echo "${color}Virtualenvwrapper is not install. Please install it first${reset}"
    exit 1
fi

echo "${color} Creating python virtual environment...${reset}"

source $(which virtualenvwrapper.sh)
mkvirtualenv tesis
workon tesis

echo "${color}Installing requirements...${reset}"
pip install -r requirements.txt
