import unittest

from puppy.simple.bunch import Bunch


class BunchTestCase(unittest.TestCase):

    def test_read(self):
        # Create a testcase bunch
        bunch = Bunch(dict(test="Hello World"))
        assert bunch.test == "Hello World"

    def test_write(self):
        # Create a testcase bunch
        bunch = Bunch(dict(test=None))
        bunch.test = "Hello World"
        assert bunch.test == "Hello World"
