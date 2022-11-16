from puppy.http.server.constants import NOT_FOUND  # NOQA


class Router(object):
    # Private routes dictionary
    _routes = dict()

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
                    self._routes[(method, location)] = function
            else:
                # Attach to a wildcard method
                self._routes[(None, location)] = function

            # Return the function with no change
            return function

        # Return wrapper
        return wrapper

    def __call__(self, request):
        # Check if has a valid route exists
        routes = [
            # Method specific route
            (request.method, request.location),
            # Method wildcard route
            (None, request.location),
        ]

        # Check if any valid route exists
        for route in routes:
            # Check if route exists in registry
            if route in self._routes:
                # Route the request
                return self._routes[route](request)

        # Return 404!
        return NOT_FOUND
