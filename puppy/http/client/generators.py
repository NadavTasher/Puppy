# Import python libraries
import json
import urllib

# Import other classes
from .classes import Body, Header
from .constants import HEADER_TYPE


def MimeType(content, mimetype):
    # Return body with mimetype
    return Body(content, [Header(HEADER_TYPE, mimetype)])


def JSON(content):
    # Validate content type
    assert isinstance(content, (dict, list, str))

    # Return mime-typed encoded body
    return MimeType(json.dumps(content), "application/json")


def Form(content):
    # Validate content type
    assert isinstance(content, dict)

    # Return mime-typed encoded body
    return MimeType(
        "&".join(
            [
				# Key-value string
                "{0}={1}".format(urllib.quote(key), urllib.quote(value))
                # For each item in the form
				for key, value in content.items()
            ]
        ),
        "application/form-data",
    )

def Multipart(strings, files):
	# Validate content type
	pass