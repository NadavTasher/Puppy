import os
import time
import json
import hmac
import base64
import hashlib
import binascii

# Import token types
from puppy.token.types import Token

# Import general utilities
from puppy.bunch import Bunch
from puppy.typing.types import Bytes, Text, Union
from puppy.typing.validator import validator

# Length of the token signature
SIGNATURE = 32


class Authority(object):

    def __init__(self, secret):
        # Set the secret
        self._secret = secret

        # Create the validator
        @validator
        def TokenType(token, *permissions):
            # Make sure token type is right
            if not isinstance(token, Union[Text, Bytes]):
                return False

            # Try validating using authority
            try:
                self.validate(token, *permissions)

                # Validation has passed
                return True
            except:
                # Validation has failed
                return False

        # Set the validator
        self.TokenType = TokenType

    def issue(self, name, contents=None, permissions=None, validity=60 * 60 * 24 * 365):
        # Make sure parameters are initialized
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

        # Replace contents with bunch
        token_object = token_object._replace(contents=Bunch(token_object.contents))

        # Encode the token and return
        return base64.b64encode(token_buffer), token_object

    def validate(self, token, *permissions):
        # Decode token to buffer
        token_buffer = base64.b64decode(token)

        # Split buffer to token string and HMAC
        token_string, token_hmac = token_buffer[:-SIGNATURE], token_buffer[-SIGNATURE:]

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

        # Replace contents with bunch
        token_object = token_object._replace(contents=Bunch(token_object.contents))

        # Return the created object
        return token_object
