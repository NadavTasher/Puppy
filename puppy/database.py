import os
import json
import hashlib
import threading
import contextlib
import collections

from puppy.bunch import MutableBunch, Bunch
from puppy.filesystem import remove

class Index(object):
	def __init__(self, path):
		# Create variables
		self.path = os.path.join(path, self.__class__.__name__.lower())
		self.lock = threading.RLock()

		# Create index if does not exist
		with self.modify():
			pass
	
	def read(self):
		# Lock the mutex
		with self.lock:
			# Make sure index exists
			if not os.path.exists(self.path):
				return set()

			# Read index contents
			with open(self.path, "r") as file:
				return set(json.load(file))

	@contextlib.contextmanager
	def modify(self):
		with self.lock:
			# Read the index
			index = self.read()
			
			# Yield for modification	
			yield index

			# Write to file
			with open(self.path, "w") as file:
				json.dump(list(index), file)

class Objects(object):
	def __init__(self, path, locks):
		# Create variables
		self.path = os.path.join(path, self.__class__.__name__.lower())
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


class Keystore(MutableBunch):
	# Define internal variables
	index = None
	objects = None

	# Define default variable
	DEFAULT = object()

	def __init__(self, path, locks):
		# Create directory if it does not exist
		if not os.path.exists(path):
			os.makedirs(path)

		# Create managing objects
		self.index = Index(path)
		self.objects = Objects(path, locks)

	def __contains__(self, key):
		# Make sure file exists
		if not os.path.exists(self.objects.read(key)):
			return False
		
		# Make sure index contains key
		return key in iter(self)

	def __getitem__(self, key):
		# Make sure key exists
		if key not in self:
			raise KeyError(key)

		# Resolve path of object
		path = self.objects.read(key)

		# Check if object is a simple object
		if os.path.isfile(path):
			# Read file contents
			with open(path, "r") as file:
				return json.load(file)

		# Create a complex object from the path
		return Keystore(path, self.objects.locks)


	def __setitem__(self, key, value):
		# Modify the object
		with self.objects.modify(key) as path:	
			# Check if value is a dictionary
			if not isinstance(value, collections.Mapping):
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
				Keystore(path, self.objects.locks).update(value)

		# Check if key needs to be added to index
		with self.index.modify() as index:
			index.add(key)

	def __delitem__(self, key):
		# Make sure key exists
		if key not in self:
			raise KeyError(key)

		# Delete item from index
		with self.index.modify() as index:
			index.discard(key)

		# Delete item from filesystem
		with self.objects.modify(key) as path:	
			remove(path)

	def __iter__(self):
		# Read the index
		for key in self.index.read():
			# Yield all the keys
			yield key

	def __len__(self):
		# Calculate the length of keys
		return len(iter(self))
		
	def keys(self):
		# Loop over keys
		for key in self:
			# Yield all the keys
			yield key

	def values(self):
		# Loop over keys
		for key in self:
			# Yield all the values
			yield self[key]

	def items(self):
		# Loop over keys
		for key in self:
			# Yield all keys and values
			yield key, self[key]

	def get(self, key):
		# Make sure key exists 
		if key not in self:
			# Return default
			return
		
		# Return the value
		return self[key]

	def pop(self, key, default=DEFAULT):
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
		# Get the key from index
		key = list(self).pop()

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

	def clear(self):
		# Loop over keys
		for key in self:
			# Delete all values
			del self[key]

	def update(self, *args, **kwargs):
		# Loop over all arguments
		for arg in args:
			# Set the argument values
			for key in arg:
				self[key] = arg[key]
		
		# Set the keyword values
		for key in kwargs:
			self[key] = kwargs[key]

	def setdefault(self, key, default=None):
		# Check if key exists
		if key not in self:
			self[key] = value

		# Return the value
		return self[key]

	def __repr__(self):
		# Format the data like a dictionary
		return "{%s}" % ", ".join("%r: %r" % item for item in self.items())

class Database(Keystore):
	def __init__(self, path):
		# Initialize the keystore with an empty locker
		super(Database, self).__init__(path, dict())