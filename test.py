import socket
from puppy.http import Browser, Options, JSON, Request, Header

s = socket.socket()
s.connect(("93.184.216.34", 80))

o = Options(False, False)
b = Browser(s, o)

print(b.post("/", {}, [Header("Host", "example.com"), Header("User-Agent", "test")]))