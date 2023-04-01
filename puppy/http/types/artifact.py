from puppy.http.types.headers import Headers


class Artifact(object):

    def __init__(self, headers=None, content=None):
        # Create artifact headers object
        self.headers = Headers(headers or list())

        # Assign artifact content
        self.content = content

    @property
    def header(self):
        pass

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.headers, self.content)


class Received(Artifact):

    def __init__(self, line, headers=None, content=None):
        # Set the internal line
        self.line = line

        # Initialize the artifact
        super(Received, self).__init__(headers, content)

    @property
    def header(self):
        return self.line

    def __repr__(self):
        return "%s(%r, %r, %r)" % (
            self.__class__.__name__,
            self.line,
            self.headers,
            self.content,
        )
