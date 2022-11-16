import collections  # NOQA

from puppy.http.constants import VERSION  # NOQA


class Artifact(object):
    def __init__(self, headers=None, content=None):
        # Set the internal contents
        self.headers = headers or Headers()
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


class Request(Artifact):
    def __init__(self, method, location, headers=None, content=None):
        # Set internal variables
        self.method = method
        self.location = location

        # Initialize the artifact
        super(Request, self).__init__(headers, content)

    @property
    def header(self):
        return "%s %s HTTP/%.1f" % (self.method.upper(), self.location, VERSION)

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.method,
            self.location,
            self.headers,
            self.content,
        )


class Response(Artifact):
    def __init__(self, status, message, headers=None, content=None):
        # Set internal variables
        self.status = status
        self.message = message

        # Initialize the artifact
        super(Response, self).__init__(headers, content)

    @property
    def header(self):
        return "HTTP/%.1f %d %s" % (VERSION, self.status, self.message)

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (
            self.__class__.__name__,
            self.status,
            self.message,
            self.headers,
            self.content,
        )


class Headers(object):
    def __init__(self, headers=[]):
        # Initialize order list
        self.store = collections.OrderedDict()

        # Add all headers
        for name, value in headers:
            self.add_header(name, value)

    def has(self, name):
        return name.decode().lower() in self.store.keys()

    def new(self, name):
        # Make sure name does not exist
        if self.has(name):
            return

        # Create new entry
        self.store[name.decode().lower()] = (name, list())

    def pop(self, name):
        try:
            # Fetch all values
            return self.fetch(name)
        finally:
            # Remove the value
            self.remove(name)

    def fetch(self, name):
        # Make sure header exists
        if not self.has(name):
            return list()

        # Fetch values from store
        _, values = self.store[name.decode().lower()]

        # Return the values
        return values

    def append(self, name, value):
        # Create new entry if does not exist
        if not self.has(name):
            self.new(name)

        # Fetch values and append to them
        values = self.fetch(name)
        values.append(value)

        # Update store values
        self.store[name.decode().lower()] = (name, values)

    def update(self, name, value):
        # Create new entry if does not exist
        if not self.has(name):
            self.new(name)

        # Update store values
        self.store[name.decode().lower()] = (name, [value])

    def remove(self, name):
        # Make sure the header exists
        if not self.has(name):
            return

        # Remove key from list and value from dict
        self.store.pop(name.decode().lower())

    def __iter__(self):
        # Loop over values and yield
        for name, values in self.store.values():
            for value in values:
                yield name, value

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(self))