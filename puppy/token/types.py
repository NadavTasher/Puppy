from puppy.namedtuple import NamedTuple
from puppy.typing.types import Any, Text, List, Dict, Optional

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