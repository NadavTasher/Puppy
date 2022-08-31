from puppy.http import Server, Response

def handle(request):
	return Response(200, "OK", [], "Hello World!")

serv = Server(("0.0.0.0", 8000), handle)
serv.start()

# s = socket.socket()
# s.connect(("127.0.0.1", 8000))

# o = Options(False, False)
# b = Browser(s, o)

# print(b.post("/", {}, [Header("Host", "example.com"), Header("User-Agent", "test")]))

serv.join()