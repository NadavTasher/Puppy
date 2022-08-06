# Import python libraries
import collections

# Import project classes
from .utilities import bind, validator
from .validators import form, string

# Create validator functions
@validator
def options(value):
    pass


@validator
def artifact(value):
    # Make sure value is an artifact
    assert isinstance(value, Artifact)

    # Make sure request is a request and response is a response
    assert isinstance(value.request, Request)
    assert isinstance(value.response, Response)


@validator
def body(value):
    # Make sure the given body is a body
    assert isinstance(value, Body)

    # Make sure content is a string
    assert isinstance(value.content, str)

    # Make sure headers are a list of headers
    if value.headers is not None:
        assert isinstance(value.headers, list)
        assert all([isinstance(header, Header) for header in value.headers])


@validator
def header(value):
    # Make sure the given header is a list
    assert isinstance(value, Header)

    # Make sure the list is of length 2
    assert len(value) == 2

    # Make sure all the values in the list are safe strings
    assert all([string(item) for item in value])


@validator
def request(value):
    # Make sure the request is a Request
    assert isinstance(value, Request)

    # Validate request method
    assert string(value.method) in ["GET", "POST"]

    # Validate request location
    assert string(value.location)

    # Validate request parameters
    if value.parameters is not None:
        # Make sure parameters are dict
        form(value.parameters)

    # Validate request headers
    if value.headers is not None:
        assert isinstance(value.headers, list)
        assert all([isinstance(header, Header) for header in value.headers])

    # Validate request body
    if value.body is not None:
        assert isinstance(value.body, Body)


@validator
def response(value):
    pass


# Create browser classes
Options = bind(options, collections.namedtuple("Options", ["linger", "compress"]))
Artifact = bind(artifact, collections.namedtuple("Artiface", ["request", "response"]))

# Create request and response parts
Body = bind(body, collections.namedtuple("Body", ["content", "headers"]))
Header = bind(header, collections.namedtuple("Header", ["name", "value"]))

# Create request & response classes
Request = bind(
    request,
    collections.namedtuple(
        "Request", ["method", "location", "parameters", "headers", "body"]
    ),
)
Response = bind(
    response,
    collections.namedtuple("Response", ["status", "message", "headers", "body"]),
)

Request("GET", "/", {}, [], Body("hello", []))
