# Import classes
from .classes import *

# Initialize operating constants
CRLF = "\r\n"

HTTP_VERSION = 1.1
HTTP_METHODS = ["GET", "POST"]

HEADER_LENGTH = "Content-Type"

REQUEST_HEADER_CLOSE = Header("Connection", "Close")
REQUEST_HEADER_LINGER = Header("Connection", "Keep-Alive")
REQUEST_HEADER_COMPRESS = Header("Accept-Encoding", "gzip")

RESPONSE_HEADER_COMPRESS = Header("")

# Initialize default options
DEFAULT_OPTIONS = Options(False, False)
