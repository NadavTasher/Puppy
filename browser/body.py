# Import python libraries
import json
import urllib


class Body(object):
    @property
    def content(self):
        # Return content
        return str()

    @property
    def headers(self):
        # Return headers
        return list()

    def __str__(self):
        # Return rendered content
        return self.content


class Mimetype(Body):
    def __init__(self, mimetype):
        # Make sure the mimetype is a string
        assert isinstance(mimetype, str)

        # Set internal mimetype
        self._mimetype = mimetype

        # Initialize parent
        super(Mimetype, self).__init__()

    @property
    def headers(self):
        # Return mimetype header
        return [("Content-Type", self._mimetype)]


class JSON(Mimetype):
    def __init__(self, content):
        # Make sure the content is a dict, list or str
        assert isinstance(content, (dict, list, str))

        # Set internal content
        self._content = content

        # Initialize parent with mimetype
        super(JSON, self).__init__("application/json")

    @property
    def content(self):
        # Convert content to JSON
        return json.dumps(self._content)


class Form(Mimetype):
    def __init__(self, content):
        # Make sure the content is a dict
        assert isinstance(content, dict)

		# Set internal content
        self._content = content
		
        # Initialize parent with mimetype
        super(Form, self).__init__("application/form-data")

    @property
    def content(self):
        # Convert content to form
        return "&".join(
            [
                # Encode as form value
                "{0}={1}".format(
                    # Encode form key
                    urllib.quote(key),
                    # Encode form value
                    urllib.quote(value),
                )
                # All values in the dictionary
                for key, value in self._content.items()
            ]
        )

class Multipart(Mimetype):
	pass
