#!/bin/bash

# - Remove all python caches
find puppy test -iname *.pyc* -exec rm {} \;
find puppy test -name __pycache__ -exec rm -r {} \;

# - Create all __init__.py files
find puppy/* test/* -type d -exec rm {}/__init__.py \;
find puppy/* test/* -type d -exec touch {}/__init__.py \;

# - Reformat all files with YAPF
yapf -ir puppy test --style "{based_on_style: google, column_limit: 400, indent_width: 4}"