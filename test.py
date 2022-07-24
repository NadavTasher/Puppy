from browser import Browser, Options, JSON

o = Options(False, True)

b = Browser(o)

b.request("POST", "/test", {"hello": "Hello World"}, JSON({"hi": "hi there"}))