import unittest

from puppy.simple.process import execute


class ProcessTestCase(unittest.TestCase):

    def test_execute(self):
        # Run simple process
        output = execute("echo -n 'Hello World'")
