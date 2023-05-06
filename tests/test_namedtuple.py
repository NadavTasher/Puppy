import unittest

from utilities import *

from puppy.simple.namedtuple import NamedTuple


class TokenTestCase(unittest.TestCase):

    def test_typecheck(self):
        # Create test class
        nt = NamedTuple("MyTest", [("hello", int)])

        # Make sure works
        a = nt(42)

        with raises(TypeError):
            b = nt("World")

    def test_repr(self):
        # Create test class
        nt = NamedTuple("MyTest", [("hello", int)])

        # Create an instance
        a = nt(42)

        # Make sure representation works
        assert repr(a) == "MyTest(hello=42)", a
