import time

from puppy.thread.future import future

class Test(object):
	@future
	def test(self, t):
		time.sleep(t)
		return "Hello"

t = Test()
v = t.test(4)
p = t.test(8)
print(~v)