# Import python libraries
from typing import Dict, List, Literal, Options, NamedTuple

# Create request and response parts
Header = NamedTuple("Header", [("name", str), ("value", str)])
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
        ("body", Optional[Body]),
    ],
)

# Create browser classes
Cookie = NamedTuple("Cookie", [("name", str), ("value", str)])
Options = NamedTuple("Options", [("linger", bool), ("compress", bool)])
Artifact = NamedTuple("Artifact", [("request", Request), ("response", Response)])
