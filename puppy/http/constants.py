# Import classes
from .types import Header, Options

# Operating constants
CRLF = "\r\n"
HTTP_VERSION = 1.1

# Common header constants
HEADER_TYPE = Header("Content-Type", str())
HEADER_LENGTH = Header("Content-Length", str())
HEADER_CLOSE = Header("Connection", "Close")
HEADER_LINGER = Header("Connection", "Keep-Alive")
HEADER_ACCEPT = Header("Accept-Encoding", "gzip")
HEADER_CHUNKED = Header("Transfer-Encoding", "chunked")
HEADER_COMPRESS = Header("Content-Encoding", "gzip")

# Initialize default options
DEFAULT_OPTIONS = Options(False, False)
