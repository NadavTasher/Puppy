import time
import logging


from puppy.http.client.client import HTTPClient
from puppy.http.server.server import HTTPServer
from puppy.http.server.router import HTTPRouter
from puppy.http.types import Response

# rtr = HTTPRouter()
# rtr.static(".")

# @rtr.get("/test")
# def handle(request):
# 	return Response(200, "OK", None, "Hello World!")

# @rtr.get("/crash")
# def h2(request):
# 	assert not request

# cli = HTTPClient()
# srv = HTTPServer(("0.0.0.0", 8000), rtr)

# try:
# 	srv.serve_forever(0.5)
# finally:
# 	srv.shutdown()

# from puppy.utilities.bpf import bpf

# print((bpf("tcp") & bpf("host 192.168.0.1")) < 200)
# from puppy.utilities.process import detached
# print(~detached("echo Hello; sleep 10", seconds=1))

# srv.join()
# print(cli.get(b"https://example.com/hello"))

from puppy.thread.machine import Machine, state

class TestMachine(Machine):
	_counter = 0

	@state
	def start_state(self):
		return self.check_state

	@state
	def check_state(self):
		if self._counter > 30:
			return self.stop_state
		
		return self.increment_state

	@state
	def increment_state(self):
		self._counter += 1
		time.sleep(0.5)
		return self.check_state, "Incremented to %d" % self._counter

logging.basicConfig(level=logging.DEBUG)

m = TestMachine()
m.start()
m.join()