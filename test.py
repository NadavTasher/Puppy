import socket
from browser import HTTP, Browser, Options, JSON
from browser.typedtuple import typedtuple

s = socket.socket()
s.connect(("93.184.216.34", 80))

o = Options(False, True)
b = HTTP(s, o)

b.request("POST", "/", {}, [], JSON({"hi": "hi there"}))