#!/bin/bash

mkvirtualenv -p /usr/bin/python3 pelican
pip install -r requirements.txt

git submodule update --init --recursive
