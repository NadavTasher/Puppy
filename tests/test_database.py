import json
import unittest
import tempfile

from utilities import raises

from puppy.simple.database import Database


class DatabaseTestCase(unittest.TestCase):

    def test_durabillity(self):
        # Create a new database
        db = Database(tempfile.mktemp())

        # Load some items into the database
        with raises(TypeError):
            db.a = dict(c="Hello", d=object())

        # Validate the database items
        assert db.a.c == "Hello"
        assert "d" not in db.a

    def test_storage(self):
        # Create a new database
        db = Database(tempfile.mktemp())

        # Make sure it is empty
        assert not db

        # Add an empty item
        db.a = {}

        # Make sure the database is not empty
        assert db

        # Load some items into the database
        db.a.b = dict(c="Hello", d={})
        db.a.b.c = "World"

        # Validate the database items
        assert db.a.b.c == "World"
        assert not db.a.b.d

    def test_bunch(self):
        # Create a new database
        db = Database(tempfile.mktemp())

        # Add some items to database
        for i in range(2):
            db["test_%d" % i] = 2**i

        # Set another item
        db.test_2 = 4

        # Check bunch features
        assert db.test_0 == 1
        assert db.test_1 == 2
        assert db.test_2 == 4

        # Delete an item
        del db.test_0

        # Check that the item does not exist
        with raises(KeyError):
            a = db.test_0

    def test_dictionary(self):
        # Create a new database
        db = Database(tempfile.mktemp())

        # Add some items to database
        for i in range(10):
            db["Hello-%d" % i] = 2**i

        # Make sure items exist
        assert "Hello-1" in db

        # Check database structure
        assert dict(db) == {'Hello-0': 1, 'Hello-1': 2, 'Hello-2': 4, 'Hello-3': 8, 'Hello-4': 16, 'Hello-5': 32, 'Hello-6': 64, 'Hello-7': 128, 'Hello-8': 256, 'Hello-9': 512}, db

    def test_serialize(self):
        # Create a new database
        db = Database(tempfile.mktemp())

        # Load some items into the database
        db.a = {}
        db.a.b = "Hello"

        # Validate the complete database
        assert dict(db) == {"a": {"b": "Hello"}}

        # Make sure the database is serializable
        assert json.dumps(db) == json.dumps({"a": {"b": "Hello"}})
