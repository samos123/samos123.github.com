#!/bin/bash

./clean.sh
pelican -s publishconf.py -o .
