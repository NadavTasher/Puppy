from puppy.http import Server, Response, HTTPInterface, HTTPConnectionStateWrapper
from puppy.thread import Looper, Process

p = Process("tcpdump -i any 'tcp'")

def handle(request):
	return Response(200, "OK", [], "".join(list(p.readlines())))

	# return Response(200, "OK", [], "Hello World!")

import socket

lp = Looper()
a = ("0.0.0.0", 8000)
serv = Server(a, handle)
serv.start()
p.start()

import time
try:
	while True:
		time.sleep(1)
finally:
	serv.stop()
	p.stop()
# s = socket.socket()
# s.connect(("127.0.0.1", 8000))

# o = Options(False, False)
# b = Browser(s, o)

# print(b.post("/", {}, [Header("Host", "example.com"), Header("User-Agent", "test")]))

serv.join()