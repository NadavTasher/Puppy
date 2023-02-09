import logging

from puppy.typing.types import *
from puppy.typing.validator import *
from puppy.database.keystore import *

# a = Bunch(a="b", c="d")
# a.d = {}
# assert "d" in a
# assert hasattr(a, "d")
# a.d.b = "hello"
# a.b = "test"
# print(a)

# b = Database("/tmp/aaab")
# b.a = {"m":"d"}
# print(type(b.a))
# print(type(b["a"]))
# b.a.b = "a"
# print(b)
# print(b.a.b)

# @validator
# def Text(value):
# 	return isinstance(value, (str, bytes, u"".__class__))

logging.warning("Type of text: %r", Text)
logging.warning("Is hello text: %r", isinstance("hello", Text))
