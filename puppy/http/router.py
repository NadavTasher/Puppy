import os

from puppy.http.types import Response
from puppy.http.utilities import split_path
from puppy.http.constants import GET, POST


class HTTPRouter(object):

    def __init__(self):
        # Private routes dictionary
        self.routes = dict()

    def add(self, location, function, *methods):
        if methods:
            for method in methods:
                # Attach function to routes
                self.routes[(method, location)] = function
        else:
            # Attach to a wildcard method
            self.routes[(None, location)] = function

    def get(self, location):
        return self.attach(location, GET)

    def post(self, location):
        return self.attach(location, POST)

    def attach(self, location, *methods):
        # Create attachment function
        def wrapper(function):
            # Attach to all required methods
            self.add(location, function, *methods)

            # Return the function with no change
            return function

        # Return wrapper
        return wrapper

    def static(self, path, name=b"/", indexes=[]):
        # Check if the path is a file
        if os.path.isfile(path):
            # Read the path ahead-of-time
            with open(path, "rb") as file:
                contents = file.read()

            # Create a lambda to the path
            self.add(name, lambda request: contents, GET)
        else:
            # Loop over paths and load them as routes
            for subname in os.listdir(path):
                # Add static file
                self.static(os.path.join(path, subname), os.path.join(name, subname), indexes)

                # If the subname matches an index, add it too
                if subname in indexes:
                    self.static(os.path.join(path, subname), name, indexes)

    def handle(self, method, path, request):
        # Try finding a handler
        for route in ((method, path), (None, path)):
            # Check if route exists in registry
            if route not in self.routes:
                continue

            # Try executing the handler
            try:
                # Store the execution result
                result = self.routes[route](request)

                # Check if the result is a response
                if isinstance(result, Response):
                    return result

                # Wrap the result in a response
                return Response(200, b"OK", [], result)
            except:
                # The route has raised an exception
                return Response(500, b"Internal Server Error", [], bytes())
        else:
            # The route was not found
            return Response(404, b"Not Found", [], bytes())

    def __call__(self, request):
        # Convert method and location
        method = request.method
        location = request.location

        # Parse the location
        path, query, fragment = split_path(location)

        # Handle the request
        return self.handle(method, path, request)
