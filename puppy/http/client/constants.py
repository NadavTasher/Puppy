# Import classes
from .classes import Header, Options

# Operating constants
CRLF = "\r\n"
HTTP_VERSION = 1.1

# Common header constants
HEADER_TYPE = "Content-Type"
HEADER_LENGTH = "Content-Length"

# Request header constants
REQUEST_HEADER_CLOSE = Header("Connection", "Close")
REQUEST_HEADER_LINGER = Header("Connection", "Keep-Alive")
REQUEST_HEADER_COMPRESS = Header("Accept-Encoding", "gzip")

# Response header constants
RESPONSE_HEADER_CHUNKED = Header("Transfer-Encoding", "chunked")
RESPONSE_HEADER_COMPRESS = Header("Content-Encoding", "gzip")

# Initialize default options
DEFAULT_OPTIONS = Options(False, False)
