# Import typing library
from ...typing import *

# Import other types
from ..types import Request, Response

# Import constants
from .constants import PROTOCOLS

# Create browser classes
URL = NamedTuple(
    "URL",
    [
        ("protocol", Literal["http", "https"]),
        ("host", str),
        ("port", int),
        ("path", str),
    ],
)
Cookie = NamedTuple("Cookie", [("name", str), ("value", str)])
Options = NamedTuple("Options", [("linger", bool), ("compress", bool)])
History = NamedTuple("History", [("request", Request), ("response", Response)])
