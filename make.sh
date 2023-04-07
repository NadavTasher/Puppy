#!/bin/bash

# - Remove all python caches
find puppy tests -iname *.pyc* -exec rm {} \;
find puppy tests -name __pycache__ -exec rm -r {} \;

# - Create all __init__.py files
find puppy/* tests/* -type d -exec rm {}/__init__.py \;
find puppy/* tests/* -type d -exec touch {}/__init__.py \;

# - Reformat all files with YAPF
yapf -ir puppy tests --style "{based_on_style: google, column_limit: 400, indent_width: 4}"