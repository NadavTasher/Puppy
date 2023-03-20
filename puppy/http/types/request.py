from puppy.http.constants import VERSION
from puppy.http.types.artifact import Artifact


class Request(Artifact):

    def __init__(self, method, location, headers=None, content=None):
        # Set internal variables
        self.method = method
        self.location = location

        # Initialize the artifact
        super(Request, self).__init__(headers, content)

    @property
    def header(self):
        return b"%s %s HTTP/%.1f" % (self.method.upper(), self.location, VERSION)

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.method,
            self.location,
            self.headers,
            self.content,
        )
