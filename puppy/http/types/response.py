from puppy.http.constants import VERSION
from puppy.http.types.artifact import Artifact


class Response(Artifact):

    def __init__(self, status, message, headers=None, content=None):
        # Set internal variables
        self.status = status
        self.message = message

        # Initialize the artifact
        super(Response, self).__init__(headers, content)

    @property
    def header(self):
        return b"HTTP/%.1f %d %s" % (VERSION, self.status, self.message)

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.status,
            self.message,
            self.headers,
            self.content,
        )
