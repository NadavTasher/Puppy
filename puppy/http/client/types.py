# Import typing library
from puppy.typing.types import Literal
from puppy.typing.namedtuple import NamedTuple

# Import other types
from puppy.http.types import Request, Response

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
History = NamedTuple("History", [("request", Request), ("response", Response)])
