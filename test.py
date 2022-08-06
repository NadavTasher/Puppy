from browser import HTTP, Browser, Options, JSON

o = Options(False, True)

b = HTTP(o)

b.request("POST", "/test", {}, [], JSON({"hi": "hi there"}))