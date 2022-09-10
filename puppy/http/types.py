# Import typing library
from ..typing import *

# Create interface classes
Options = NamedTuple("Options", [("linger", bool), ("compress", bool)])
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

# Create browser classes
Cookie = NamedTuple("Cookie", [("name", str), ("value", str)])
History = NamedTuple("History", [("request", Request), ("response", Response)])

# Create interface and wrapper types
class Interface(object):
    def __init__(self):
        pass

    def receive(self):
        raise NotImplementedError()

    def transmit(self, argument):
        raise NotImplementedError()


class Wrapper(Interface):
    def __init__(self, interface):
        # Initialize parent class
        super(Wrapper, self).__init__()

        # Set internal variable
        self._interface = interface