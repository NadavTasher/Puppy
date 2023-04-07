import base64
import unittest

from utilities import *

from puppy.token.authority import Authority
from puppy.token.exceptions import PermissionError, ExpirationError, SignatureError


class TokenTestCase(unittest.TestCase):

    def test_basic(self):
        # Create authority
        authority = Authority(b"123456")

        # Generate token
        token_string, token_object = authority.issue("Test Token", {"test": 1}, ["test"])

        # Validate token
        authority.validate(token_string, "test")

    def test_permissions(self):
        # Create authority
        authority = Authority(b"123456")

        # Generate token
        token_string, token_object = authority.issue("Test Token", {"test": 1}, ["test"])

        # Check permission validation
        with raises(PermissionError):
            authority.validate(token_string, "hello")

    def test_expiration(self):
        # Create authority
        authority = Authority(b"123456")

        # Check token expiration
        token_string, token_object = authority.issue("Test Token", {"test": 1}, ["test"], -1)

        # Check expiration validation
        with raises(ExpirationError):
            authority.validate(token_string, "test")

    def test_signature(self):
        # Create authority
        authority = Authority(b"123456")

        # Check token signature
        token_string, token_object = authority.issue("Test Token", {"test": 1}, ["test"])

        # Add byte to string
        token_string = base64.b64encode(base64.b64decode(token_string) + b"\x00")

        # Check signature validation
        with raises(SignatureError):
            authority.validate(token_string, "test")
