from puppy.http.server.constants import NOT_FOUND  # NOQA


class Router(object):
    # Private routes dictionary
    _routes = dict()

    def get(self, path):
        return self.attach(path, "GET")

    def post(self, path):
        return self.attach(path, "POST")

    def attach(self, path, *methods):
        # Create attachment function
        def wrapper(function):
            # Attach to all required methods
            if methods:
                for method in methods:
                    # Attach function to routes
                    self._routes[(method, path)] = function
            else:
                # Attach to a wildcard method
                self._routes[(None, path)] = function

            # Return the function with no change
            return function

        # Return wrapper
        return wrapper

    def __call__(self, request):
        # Check if has a valid route exists
        routes = [
            # Method specific route
            (request.method, request.path),
            # Method wildcard route
            (None, request.path),
        ]

        # Check if any valid route exists
        for route in routes:
            # Check if route exists in registry
            if route in self._routes:
                # Route the request
                return self._routes[route](request)

        # Return 404!
        return NOT_FOUND
