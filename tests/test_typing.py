import unittest

from puppy.typing.types import *


class TypingTestCase(unittest.TestCase):

    def test_any(self):
        assert isinstance(None, Any)
        assert isinstance("Hello World", Any)

    def test_union(self):
        assert isinstance("Hello World", Union[Text, int])
        assert isinstance(42, Union[Text, int])
        assert not isinstance(42.0, Union[Text, int])

    def test_intersection(self):
        assert isinstance("hello@localhost", Intersection[Text, Email])
        assert not isinstance("hello", Intersection[Text, Email])

    def test_literal(self):
        assert isinstance("Hello World", Literal["Hello World", 42])
        assert isinstance(42, Literal["Hello World", 42])
        assert not isinstance("Test", Literal["Hello World", 42])

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

    def test_list(self):
        assert isinstance(["Hello", "World", 42], List)
        assert not isinstance(["Hello", "World", 42], List[Text])

    def test_dict(self):
        assert isinstance({"hello": "world", "test": "test"}, Dict[str, str])
        assert not isinstance({"hello": "world", "test": 42}, Dict[str, str])

    def test_tuple(self):
        assert isinstance((1, 2, 3), Tuple[int, int, int])
        assert isinstance((1, 2, 3, "Hello World"), Tuple[int, int, int, Text])
        assert not isinstance((1, 2, 3, "Hello World"), Tuple[int, int, int, int])
        assert not isinstance("Hello World", Tuple[int, int, int])

    def test_schema(self):
        assert isinstance({"hello": "World", "number": 42, "boolean": True, "list-of-names": ["Jack", "James", "John"], "mapping-of-numbers": {42: "Meaning of life", 3.14: "Value of Pi"}}, Schema[{"hello": Text, "number": int, "boolean": bool, "list-of-names": List[Text], "mapping-of-numbers": Dict[Union[int, float], Text]}])
        assert not isinstance({"hello": "World", "number": 42, "boolean": True, "list-of-names": ["Jack", "James", "John"], "mapping-of-numbers": {42: "Meaning of life", 3.14: "Value of Pi", "Test": "Hello World"}}, Schema[{"hello": Text, "number": int, "boolean": bool, "list-of-names": List[Text], "mapping-of-numbers": Dict[Union[int, float], Text]}])

    def test_charset(self):
        assert isinstance("Hello World", Charset["HeloWrd "])
        assert not isinstance("Test", Charset["HeloWrd "])

    def test_domain(self):
        assert isinstance("localhost", Domain)
        assert isinstance("local.host", Domain)
        assert not isinstance("", Domain)
        assert not isinstance(".", Domain)
        assert not isinstance(".host", Domain)
        assert not isinstance("local.", Domain)

    def test_email(self):
        assert isinstance("hello.world@localhost", Email)
        assert isinstance("hello@local.host", Email)
        assert not isinstance(".hello@localhost", Email)
        assert not isinstance("@local.host", Email)
        assert not isinstance(".@local.host", Email)
        assert not isinstance("hello.world@", Email)
        assert not isinstance("hello.world@.", Email)

    def test_id(self):
        assert isinstance("asdasdasd", ID)
        assert not isinstance("asdasdasd=", ID)

    def test_binary(self):
        assert isinstance("00101101", Binary)
        assert not isinstance("00101102", Binary)

    def test_decimal(self):
        assert isinstance("1234", Decimal)
        assert not isinstance("0x1234", Decimal)

    def test_hexadecimal(self):
        assert isinstance("badc0ffe", Hexadecimal)
        assert not isinstance("badcoffe", Hexadecimal)
