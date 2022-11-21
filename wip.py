import time

from puppy.http.client.client import HTTPClient
from puppy.http.server.server import HTTPServer
from puppy.http.server.router import HTTPRouter
from puppy.http.types import Response

rtr = HTTPRouter()
rtr.static(".")

@rtr.get("/test")
def handle(request):
	return Response(200, "OK", None, "Hello World!")

@rtr.get("/crash")
def h2(request):
	assert not request

cli = HTTPClient()
srv = HTTPServer(("0.0.0.0", 8000), rtr)

# try:
# 	srv.serve_forever(0.5)
# finally:
# 	srv.shutdown()

# from puppy.utilities.bpf import bpf

# print((bpf("tcp") & bpf("host 192.168.0.1")) < 200)
# from puppy.utilities.process import detached
# print(~detached("echo Hello; sleep 10", seconds=1))

# srv.join()
print(cli.get(b"https://example.com/hello"))
