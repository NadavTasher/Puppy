# Import threading classes
from threading import Thread, Event, Lock

class Looper(Thread):
	_lock = Lock()
	_event = Event()
	_parent = None

	def initialize(self):
		pass

	def finalize(self):
		pass

	@property
	def running(self):
		pass

	def run(self):
		pass
	