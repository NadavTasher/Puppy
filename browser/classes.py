# Import python libraries
from .typedtuple import *

# Create request and response parts
Header = typedtuple("Header", [("name", str), ("value", str)])
Body = typedtuple("Body", [("content", str), ("headers", Optional(List(Header)))])

# Create request & response classes
Request = typedtuple(
    "Request",
    [
        ("method", Literal("GET", "POST")),
        ("location", str),
        ("parameters", Optional(Dictionary(str, str))),
        ("headers", Optional(List(Header))),
        ("body", Optional(Body)),
    ],
)
Response = typedtuple(
    "Response",
    [
        ("status", int),
        ("message", str),
        ("headers", List(Header)),
        ("body", Optional(Body)),
    ],
)

# Create browser classes
Cookie = typedtuple("Cookie", [("name", str), ("value", str)])
Options = typedtuple("Options", [("linger", bool), ("compress", bool)])
Artifact = typedtuple("Artifact", [("request", Request), ("response", Response)])
