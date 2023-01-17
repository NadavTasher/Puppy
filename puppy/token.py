import os
import time
import json
import hmac
import base64
import hashlib
import binascii

from puppy.namedtuple import NamedTuple
from puppy.typing.types import Any, Text, List, Dict, Optional

# Class to store tokens
Token = NamedTuple(
    "Token",
    [
        ("id", Text),
        ("name", Text),
        ("contents", Dict[Text, Any]),
        ("validity", int),
        ("timestamp", int),
        ("permissions", List[Text]),
    ],
)


class Authority(object):

    def __init__(self, secret):
        # Set the secret
        self._secret = secret

    def issue(self, name, contents=None, permissions=None, validity=60 * 60 * 24 * 365):
        # Make sure all parameters are initialized
        contents = contents or dict()
        permissions = permissions or list()

        # Calculate token validity
        timestamp = int(time.time())

        # Create identifier
        identifier = binascii.b2a_hex(os.urandom(10)).decode()

        # Create token object and string
        token_object = Token(identifier, name, contents, timestamp + validity, timestamp, permissions)
        token_string = json.dumps(token_object).encode()
        token_hmac = hmac.new(self._secret, token_string, hashlib.sha256).digest()

        # Calculate token HMAC and create buffer
        token_buffer = token_string + token_hmac

        # Encode the token and return
        return base64.b64encode(token_buffer), token_object

    def validate(self, token, *permissions):
        # Decode token to buffer
        token_buffer = base64.b64decode(token)

        # Split buffer to token string and HMAC
        token_string, token_hmac = token_buffer[:-32], token_buffer[-32:]

        # Validate HMAC of buffer
        assert (hmac.new(self._secret, token_string, hashlib.sha256).digest() == token_hmac), "Token HMAC is invalid"

        # Decode string to token object
        token_object = Token(*json.loads(token_string.decode()))

        # Validate the expiration dates
        assert token_object.timestamp < time.time(), "Token timestamp is invalid"
        assert token_object.validity > time.time(), "Token validity is expired"

        # Validate permissions
        for permission in permissions:
            assert permission in token_object.permissions, ("Token is missing the %r permission" % permission)

        # Return the created object
        return token_object
