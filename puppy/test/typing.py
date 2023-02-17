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

    def test_text(self):
        assert isinstance("Hello World", Text)
        assert isinstance(u"Hello World", Text)
        assert not isinstance(0, Text)

    def test_bytes(self):
        assert isinstance(b"Hello World", Bytes)
        assert not isinstance(0, Bytes)
