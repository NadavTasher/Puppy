# Version constant
VERSION = b"1.1"

# Operating constants
CR = b"\r"
LF = b"\n"
CRLF = CR + LF
BYTES = b"%s"
INTEGER = b"%d"
SEPARATOR = b":"
WHITESPACE = b" "

# Method constants
GET = b"GET"
POST = b"POST"

# Artifact headers
REQUEST = BYTES + WHITESPACE + BYTES + WHITESPACE + b"HTTP/" + VERSION
RESPONSE = b"HTTP/" + VERSION + WHITESPACE + INTEGER + WHITESPACE + BYTES

# Header constants
HOST = b"Host"
COOKIE = b"Cookie"
SET_COOKIE = b"Set-Cookie"
CONNECTION = b"Connection"
CONTENT_TYPE = b"Content-Type"
CONTENT_LENGTH = b"Content-Length"
ACCEPT_ENCODING = b"Accept-Encoding"
CONTENT_ENCODING = b"Content-Encoding"
TRANSFER_ENCODING = b"Transfer-Encoding"

# Value constants
GZIP = b"gzip"
CLOSE = b"close"
CHUNKED = b"chunked"
KEEP_ALIVE = b"keep-alive"

# Path splitting constants
PORT = b":"
PATH = b"/"
QUERY = b"?"
SCHEMA = b"://"
FRAGMENT = b"#"