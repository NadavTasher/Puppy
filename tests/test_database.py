import os
import json
import unittest
import tempfile

from utilities import raises

from puppy.simple.database import Database, FileSystemMutableMapping, Python, JSON


class DatabaseTestCase(unittest.TestCase):

    def test_filesystem_mutable_mapping(self):
        # Create a new mutable mapping
        db = FileSystemMutableMapping(tempfile.mktemp())

        # Try loading an item into the db
        db._test_item = b"Hello!"

        # Try loading a bad item
        with raises(TypeError):
            db._test_item_2 = 10

        # Try loading in invalid path
        with raises(TypeError):
            db["Hello|World"] = b"Test!"

        # Make sure database structure is ok
        assert db._test_item == b"Hello!"
        assert "_test_item_2" not in db
        assert "Hello|World" not in db

    def test_durabillity_python(self):
        # Create a new database
        db = Database(tempfile.mktemp(), Python)

        # Insert some subdict into the db
        db.subdict = dict(Hello="World")

        # Make sure there are objects in the db
        assert set(os.listdir(db._keys._objects_path)) == {'c66065be8268c074f0eb9c83423297bb5533e9f194f2995a736606a1698a9ffc', '7c9078aaabaee288341067544d27c1838aa5fe3b1bc4964d4c056b9bb388574e', '46e93f1a1f742b32d8ef751cdf4e2c5a8465bc88476cbfb19f3a77635947f0a9'}

        # Delete the subdict and check again
        del db.subdict

        # Make sure there are no objects in the db
        assert not len(os.listdir(db._keys._objects_path))

    def test_durabillity_json(self):
        # Create a new database
        db = Database(tempfile.mktemp(), JSON)

        # Insert some subdict into the db
        db.subdict = dict(Hello="World")

        # Make sure there are objects in the db
        assert set(os.listdir(db._keys._objects_path)) == {'c25bf945aaff8fe16826d3c1ef117044d6cc1af8e0e9f0b4162308460a8207a7', 'c102685369c5e29182d7457bd5af52486928280f000dfe641db598b82c5753e0', '835e3cc48646d9fd4114d9cfb003dc85e1670a985563c4897ba6371908644326'}

        # Delete the subdict and check again
        del db.subdict

        # Make sure there are no objects in the db
        assert not len(os.listdir(db._keys._objects_path))

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
