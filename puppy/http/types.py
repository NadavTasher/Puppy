# Import typing library
from ..typing import *

# Create interface classes
Header = NamedTuple("Header", [("name", str), ("value", str)])
Artifact = NamedTuple(
    "Artifact", [("header", str), ("headers", List[Header]), ("content", Optional[str])]
)

# Create request & response classes
Request = NamedTuple(
    "Request",
    [
        ("host", str),
        ("method", Literal["GET", "POST"]),
        ("location", str),
        ("parameters", Optional[Dict[str, str]]),
        ("headers", Optional[List[Header]]),
        ("content", Optional[str]),
    ],
)
Response = NamedTuple(
    "Response",
    [
        ("status", int),
        ("message", str),
        ("headers", List[Header]),
        ("content", Optional[str]),
    ],
)