from puppy.typing.types import Any, Text, List, Dict
from puppy.simple.namedtuple import NamedTuple

Token = NamedTuple(
    "Token",
    [
        ("id", Text),
        ("name", Text),
        ("contents", Dict[Text, Any]),
        ("validity", int),
        ("timestamp", int),
        ("permissions", List[Text]),
    ],
)