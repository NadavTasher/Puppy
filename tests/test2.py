import time
import logging
from puppy.utilities.context import contextmanager
from puppy.thread.future import future
from puppy.packer.packer import pyzip
from puppy.utilities.logging import setup

setup(__name__)

@contextmanager
def thing():
	raise Exception("Hello")

	yield


@future
def thing2(aaa):
	time.sleep(3)
	print(aaa)
	raise Exception("Shhit ")
	return aaa + "a"

logging.info("Hello")

pyzip("testz.py", ".", "python test.py")