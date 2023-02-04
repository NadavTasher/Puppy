import os
import json
import hashlib
import threading
import contextlib

from puppy.filesystem import remove
from puppy.bunch import MutableBunchMapping, Mapping, Bunch

class Node(object):
	def __init__(self, path):
		# Create the node's path
		self.path = os.path.join(path, self.__class__.__name__.lower())

class Index(Node):
	def __init__(self, path):
		# Initialize node
		super(Index, self).__init__(path)

		# Create index file lock
		self.lock = threading.RLock()

		# Create index if does not exist
		with self.modify():
			pass
	
	def read(self):
		# Lock the mutex
		with self.lock:
			# Make sure index exists
			if not os.path.exists(self.path):
				return list()

			# Read index contents
			with open(self.path, "r") as file:
				return json.load(file)

	@contextlib.contextmanager
	def modify(self):
		with self.lock:
			# Read the index
			index = self.read()
			
			# Yield for modification	
			yield index

			# Write to file
			with open(self.path, "w") as file:
				json.dump(index, file)

class Objects(Node):
	def __init__(self, path, locks):
		# Initialize node
		super(Objects, self).__init__(path)
		
		# Set the lock dictionary
		self.locks = locks

		# Create objects path if it does not exist
		if not os.path.exists(self.path):
			os.makedirs(self.path)

	def read(self, name):
		return os.path.join(self.path, hashlib.sha256(name.encode()).hexdigest())
	
	@contextlib.contextmanager
	def modify(self, name):
		# Create the path
		path = self.read(name)

		# Check mutex for name if it does not exist
		if path not in self.locks:
			self.locks[path] = threading.RLock()

		# Lock the mutex
		with self.locks[path]:
			# Yield the object path
			yield path


class Keystore(MutableBunchMapping):
	# Define internal variables
	_index = None
	_objects = None

	# Define default variable
	_DEFAULT = object()

	def __init__(self, path, locks):
		# Create directory if it does not exist
		if not os.path.exists(path):
			os.makedirs(path)

		# Create managing objects
		self._index = Index(path)
		self._objects = Objects(path, locks)

	def __contains__(self, key):
		# Make sure file exists
		if not os.path.exists(self._objects.read(key)):
			return False
		
		# Make sure index contains key
		return key in iter(self)

	def __getitem__(self, key):
		# Make sure key exists
		if key not in self:
			raise KeyError(key)

		# Resolve path of object
		path = self._objects.read(key)

		# Check if object is a simple object
		if os.path.isfile(path):
			# Read file contents
			with open(path, "r") as file:
				return json.load(file)

		# Create a complex object from the path
		return Keystore(path, self._objects.locks)


	def __setitem__(self, key, value):
		# Modify the object
		with self._objects.modify(key) as path:	
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
				Keystore(path, self._objects.locks).update(value)

		# Check if key needs to be added to index
		with self._index.modify() as index:
			if key not in index:
				index.append(key)

	def __delitem__(self, key):
		# Make sure key exists
		if key not in self:
			raise KeyError(key)

		# Delete item from index
		with self._index.modify() as index:
			if key in index:
				index.remove(key)

		# Delete item from filesystem
		with self._objects.modify(key) as path:	
			remove(path)

	def __iter__(self):
		# Read the index
		for key in self._index.read():
			# Yield all the keys
			yield key

	def __len__(self):
		# Calculate the length of keys
		return len(list(iter(self)))

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
		# Initialize the keystore with an empty locker
		super(Database, self).__init__(path, dict())