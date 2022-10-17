import time
from puppy.utilities.context import contextmanager
from puppy.thread.future import future

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


f = thing2("Hello ")
time.sleep(10)
print(f.result)