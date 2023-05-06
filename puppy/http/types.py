import collections

from puppy.typing.types import List, Tuple, Bytes, Optional
from puppy.simple.namedtuple import NamedTuple

Header = Tuple[Bytes, Bytes]
Artifact = NamedTuple("Artifact", [("header", Bytes), ("headers", List[Header]), ("content", Optional[Bytes])])
Request = NamedTuple("Request", [("method", Bytes), ("location", Bytes), ("headers", List[Header]), ("content", Optional[Bytes])])
Response = NamedTuple("Response", [("status", int), ("message", Bytes), ("headers", List[Header]), ("content", Optional[Bytes])])