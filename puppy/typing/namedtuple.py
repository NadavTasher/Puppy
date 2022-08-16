# Import collections for namedtuple
import collections

# Import types for type checking
from .types import Any, List, Tuple
from .check import types
from .validator import validate


@types(str, List[Tuple[str, Any]])
def NamedTuple(name, fields):
    # Create namedtuple classtype
    classtype = collections.namedtuple(name, [key for key, _ in fields])

    # Create class that will validate the types
    class namedtuple(classtype):
        def __new__(cls, *args, **kwargs):
            # Initialize namedtuple with values
            self = classtype.__new__(cls, *args, **kwargs)

            # Loop over properties and validate inputs
            for key, validator in fields:
                # Check input with validator
                validate(getattr(self, key), validator)

            # Initialize the tuple
            return self

    # Return created tuple
    return namedtuple
