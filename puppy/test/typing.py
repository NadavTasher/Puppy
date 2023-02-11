import unittest

from puppy.typing.types import *

class TypingTestCase(unittest.TestCase):
	def test_any(self):
		assert isinstance(None, Any)
		assert isinstance("Hello World", Any)

	def test_optional(self):
		assert isinstance(None, Optional[Text])
		assert isinstance("Hello World", Optional[Text])
		assert not isinstance(0, Optional[Text])