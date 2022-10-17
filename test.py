from puppy.http import HTTPClient, HTTPServer, Request, Response, HTTPInterface, HTTPConnectionStateWrapper
from puppy.thread import Looper, Process
from puppy.test.mock import Mock
from puppy.typing import wrapper
from puppy.io.socket.limited import limited

p = Process("tcpdump -i any 'tcp and port 8000'")

def handle(request):
	if request.parameters and "limit" in request.parameters:
		lines = p.readlines()[:int(request.parameters["limit"])]
	else:
		lines = list(p.readlines())
	return Response(200, "OK", [], "".join(lines))

	# return Response(200, "OK", [], "Hello World!")

import socket

lp = Looper()
a = ("0.0.0.0", 8000)
serv = HTTPServer(a, handle)
# serv.start()
# p.start()

# import time
# try:
# 	# while True:
# 	# 	time.sleep(1)
# 	time.sleep(1)
# 	s = socket.socket()
# 	s.connect(("93.184.216.34", 80))
# 	s2 = Mock(s)
# 	cli = HTTPClient(s2)
# 	print(cli.request("GET", "/", "example.com"))
# finally:
# 	time.sleep(1)
# 	serv.stop()
# 	p.stop()

client = HTTPClient()

class printer(wrapper):
	def socket(self, address):
		return limited(self.target.socket(address), upstream=2000, downstream=8000, exceptions=False)

	def request(self, *args, **kwargs):
		print(self, args, kwargs)
		return self.rebound.request(*args, **kwargs)

	def get(self, *args, **kwargs):
		print("Interrupted!")
		return self.rebound.get(*args, **kwargs)

client2 = printer(client)

print(client2.get("http://example.com/"))


# o = Options(False, False)
# b = Browser(s, o)

# print(b.post("/", {}, [Header("Host", "example.com"), Header("User-Agent", "test")]))

# serv.join()