import time
from puppy.utilities.context import contextmanager
from puppy.thread.future import future
from puppy.packer.packer import pyzip

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

pyzip("testz.py", ".", "python test.py")