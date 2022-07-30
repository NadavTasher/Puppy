# Import python libraries
import collections

# Create browser classes
Options = collections.namedtuple("Options", ["linger", "compress"])

# Create request & response parts
Body = collections.namedtuple("Body", ["content", "headers"])
Header = collections.namedtuple("Header", ["name", "value"])

# Create request & response classes
Request = collections.namedtuple("Request", ["method", "location", "parameters", "headers", "body"])
Response = collections.namedtuple("Response", ["status", "message", "headers", "body"])