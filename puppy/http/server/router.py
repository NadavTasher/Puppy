import os  # NOQA

from puppy.http.types import Response  # NOQA
from puppy.http.utilities import pathsplit  # NOQA
from puppy.http.server.constants import NOT_FOUND, INTERNAL_ERROR  # NOQA


class Router(object):
    def __init__(self):
        # Private routes dictionary
        self.routes = dict()

    def get(self, location):
        return self.attach(location, "GET")

    def post(self, location):
        return self.attach(location, "POST")

    def attach(self, location, *methods):
        # Create attachment function
        def wrapper(function):
            # Attach to all required methods
            if methods:
                for method in methods:
                    # Attach function to routes
                    self.routes[(method, location)] = function
            else:
                # Attach to a wildcard method
                self.routes[(None, location)] = function

            # Return the function with no change
            return function

        # Return wrapper
        return wrapper

    def files(self, path, name="/"):
        # Check if the path is a file
        if os.path.isfile(path):
            # Create a lambda to the path
            @self.get(name)
            def handler(request):
                with open(path, "rb") as file:
                    return Response(200, "OK", [], file.read())

        else:
            # Loop over paths and load them as routes
            for subname in os.listdir(path):
                self.files(os.path.join(path, subname), os.path.join(name, subname))

    def __call__(self, request):
        # Convert method and location
        method = request.method.decode()
        location = request.location.decode()

        # Parse the location
        path, query, fragment = pathsplit(location)

        # Check if has a valid route exists
        routes = [
            # Method specific route
            (method, path),
            # Method wildcard route
            (None, path),
        ]

        # Check if any valid route exists
        for route in routes:
            # Check if route exists in registry
            if route in self.routes:
                try:
                    # Route the request
                    return self.routes[route](request)
                except:
                    # Return 500!
                    return INTERNAL_ERROR

        # Return 404!
        return NOT_FOUND
