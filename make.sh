#!/bin/bash

# - Remove all python caches
find puppy -iname *.pyc* -exec rm {} \;
find puppy -name __pycache__ -exec rm -r {} \;

# - Create all __init__.py files
find puppy/* -type d -exec rm {}/__init__.py \;
find puppy/* -type d -exec touch {}/__init__.py \;

# - Reformat all files with YAPF
yapf -ir puppy --style "{based_on_style: google, column_limit: 400, indent_width: 4}"