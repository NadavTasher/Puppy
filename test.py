# import socket
# from browser import HTTP, Browser, Options, JSON, Request
# from browser.typedtuple import typedtuple

# s = socket.socket()
# s.connect(("93.184.216.34", 80))

# o = Options(False, True)
# b = HTTP(s, o)

# # print(b.request("POST", "/", {}, [], JSON({"hi": "hi there"})))
# print(Request("GET", "/", {"aaaa": "strassadasda"}, [], None))

from puppy.typing import *

# Dict[str, str]({"a": 1})

Test = NamedTuple("AAA", [("hello", int)])

print(Test("a"))