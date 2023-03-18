import os
import json
import hashlib
import functools

from puppy.bunch import MutableBunchMapping, Mapping, Bunch
from puppy.filesystem import remove


class Keystore(MutableBunchMapping):

    # Initialize variables
    _path = None
    _dictionary = None

    # Define default variable
    _DEFAULT = object()

    def __init__(self, path, dictionary):
        # Create directories if they do not exist
        for directory in (path, dictionary):
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Set internal parameters
        self._path = path
        self._dictionary = dictionary

    def _to_path(self, key):
        # Write translation as needed
        self._write_translation(key)

        # Convert key to path
        return os.path.join(self._path, self._to_checksum(self._to_bytes(key)))

    def _to_key(self, translation):
        # Convert bytes to key
        return eval(translation.decode())

    def _to_bytes(self, key):
        # Try hashing the key
        hash(key)

        # Convert key to bytes
        return repr(key).encode()

    def _to_checksum(self, raw):
        # Calculate checksum of key
        return hashlib.sha256(raw).hexdigest()

    def _to_translation(self, checksum):
        # Convert checksum to path
        return os.path.join(self._dictionary, checksum)

    def _read_translation(self, checksum):
        # Create translation path
        path = os.path.join(self._dictionary, checksum)

        # Make sure translation exists
        if not os.path.exists(path):
            raise KeyError(checksum)

        # Read translation from file
        with open(path, "rb") as file:
            translation = file.read()

        # Make sure checksum matches
        if checksum != self._to_checksum(translation):
            raise ValueError(checksum)

        # Convert back to key
        return self._to_key(translation)

    def _write_translation(self, key):
        # Create raw key
        raw = self._to_bytes(key)

        # Create translation path
        path = os.path.join(self._dictionary, self._to_checksum(raw))

        # Make sure checksum does not exist
        if os.path.exists(path):
            return

        # Write translation to file
        with open(path, "wb") as file:
            file.write(raw)

    def __contains__(self, key):
        # Check if file exists
        return os.path.exists(self._to_path(key))

    def __getitem__(self, key):
        # Make sure key exists
        if key not in self:
            raise KeyError(key)

        # Resolve path of object
        path = self._to_path(key)

        # Check if object is a simple object
        if os.path.isfile(path):
            # Read file contents
            with open(path, "r") as file:
                return json.load(file)

        # Create a complex object from the path
        return Keystore(path, self._dictionary)

    def __setitem__(self, key, value):
        # Find the path to the key
        path = self._to_path(key)

        # Check if value is a dictionary
        if not isinstance(value, Mapping):
            # Make sure value is JSON seriallizable
            json.dumps(value)

            # Delete the old value
            remove(path)

            # Write the object data as string
            with open(path, "w") as file:
                json.dump(value, file)
        else:
            # Delete the old value
            remove(path)

            # Create a new keystore
            Keystore(path, self._dictionary).update(value)

    def __delitem__(self, key):
        # Make sure key exists
        if key not in self:
            raise KeyError(key)

        # Remove the path
        remove(self._to_path(key))

    def __iter__(self):
        # List all of the items in the path
        for checksum in os.listdir(self._path):
            # Open the translation for reading
            yield self._read_translation(checksum)

    def __len__(self):
        # Calculate the length of keys
        return len(os.listdir(self._path))

    def __eq__(self, other):
        # Make sure the other object is a mapping
        if not isinstance(other, Mapping):
            return False

        # Make sure all keys exist
        if set(self.keys()) != set(other.keys()):
            return False

        # Make sure all the values equal
        for key in self:
            if self[key] != other[key]:
                return False

        # Comparison succeeded
        return True

    def __repr__(self):
        # Format the data like a dictionary
        return "{%s}" % ", ".join("%r: %r" % item for item in self.items())

    def pop(self, key, default=_DEFAULT):
        try:
            # Fetch the value
            value = self[key]

            # Check if the value is a keystore
            if isinstance(value, Keystore):
                value = value.copy()

            # Delete the item
            del self[key]

            # Return the value
            return value
        except KeyError:
            # Check if a default is defined
            if default != Keystore.DEFAULT:
                return default

            # Reraise exception
            raise

    def popitem(self):
        # Convert self to list
        keys = list(self)

        # If the list is empty, raise
        if not keys:
            raise KeyError()

        # Pop a key from the list
        key = keys.pop()

        # Return the key and the value
        return key, self.pop(key)

    def copy(self):
        # Create initial bunch
        output = Bunch()

        # Loop over keys
        for key in self:
            # Fetch value of key
            value = self[key]

            # Check if value is a keystore
            if isinstance(value, Keystore):
                value = value.copy()

            # Update the bunch
            output[key] = value

        # Return the created output
        return output


class Database(Keystore):

    def __init__(self, path):
        # Create the directory
        if not os.path.exists(path):
            os.makedirs(path)

        # Create keystore and dictionary paths
        database = os.path.join(path, "database")
        dictionary = os.path.join(path, "dictionary")

        # Initialize the keystore with an empty locker
        super(Database, self).__init__(database, dictionary)


class Encoder(json.JSONEncoder):

    def default(self, obj):
        # Check if the object is a keystore
        if isinstance(obj, Keystore):
            # Return a JSON encodable representation of the keystore
            return obj.copy()

        # Fallback default
        return super(Encoder, self).default(obj)


# Update the default dumps function
json.dump = functools.partial(json.dump, cls=Encoder)
json.dumps = functools.partial(json.dumps, cls=Encoder)
