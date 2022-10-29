import os  # NOQA
import sys  # NOQA

# Add puppy to path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Try importing puppy utilities for tests
from puppy.utilities.log import setup
from puppy.utilities.path import mktemp

import tempfile # NOQA
import threading # NOQA
import subprocess  # NOQA

def run_test(name, python):
	pass

def run(version="2"):
	



	# Try running all the tests
	for name in os.listdir("tests"):
		# Run test in subprocess and wait for result
		pass