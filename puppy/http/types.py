# Import typing library
from ..typing import *

# Create HTTP artifact classes
Header = NamedTuple("Header", [("name", str), ("value", str)])
Artifact = NamedTuple(
    "Artifact", [("header", str), ("headers", List[Header]), ("content", Optional[str])]
)

# Create request and response parts
Body = NamedTuple("Body", [("content", str), ("headers", Optional[List[Header]])])

# Create request & response classes
Request = NamedTuple(
    "Request",
    [
        ("method", Literal["GET", "POST"]),
        ("location", str),
        ("parameters", Optional[Dict[str, str]]),
        ("headers", Optional[List[Header]]),
        ("body", Optional[Body]),
    ],
)
Response = NamedTuple(
    "Response",
    [
        ("status", int),
        ("message", str),
        ("headers", List[Header]),
        ("body", Optional[str]),
    ],
)

# Create browser classes
Cookie = NamedTuple("Cookie", [("name", str), ("value", str)])
Options = NamedTuple("Options", [("linger", bool), ("compress", bool)])
History = NamedTuple("History", [("request", Request), ("response", Response)])
