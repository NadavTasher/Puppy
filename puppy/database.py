import os
import json
import hashlib
import threading
import contextlib

from puppy.bunch import Bunch
from puppy.filesystem import remove

class Object(object):
	def __init__(self, path):
		self.path = path

class Index(object):
	def __init__(self, path):
		# Initialize parent
		super(Index, self).__init__(path)

		# Create variables
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

class Objects(Object):
	def __init__(self, path):
		# Initialize parent
		super(Objects, self).__init__(path)

		# Create variables
		self.locks = dict()

		# Create objects path if it does not exist
		if not os.path.exists(self.path):
			os.makedirs(self.path)

	def lock(self, name):
		# Check mutex for name if it does not exist
		if name not in self.locks:
			self.locks[name] = threading.RLock()

		# Return the lock for the name
		return self.locks[name]

	def read(self, name):
		return os.path.join(self.path, hashlib.sha256(name.encode()).hexdigest())
	
	@contextlib.contextmanager
	def modify(self, name):
		# Lock the mutex
		with self.lock(name):
			# Yield the combined path
			yield self.read(name)


class Keystore(Bunch):
	# Define internal variables
	path = None
	index = None
	objects = None

	def __init__(self, path):
		# Create indexes
		self.path = path

		# Create objects path if it does not exist
		if not os.path.exists(self.path):
			os.makedirs(self.path)

		self.index = Index(os.path.join(path, "index"))
		self.objects = Objects(os.path.join(path, "objects"))

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
		return self.__class__(path)


	def __setitem__(self, key, value):
		# Modify the object
		with self.objects.modify(key) as path:	
			# Check if value is a dictionary
			if not isinstance(value, dict):
				# Make sure value is JSON seriallizable
				json.dumps(value)

				# Write the object data as string
				with open(path, "w") as file:
					json.dump(value, file)
			else:
				# Delete the old value
				if key in self:
					del self[key]

				# Create a new keystore
				self.__class__(path).update(value)

		# Check if key needs to be added to index
		if key not in self:
			with self.index.modify() as index:
				if key not in index:
					index.append(key)

	def __delitem__(self, key):
		# Make sure key exists
		if key not in self:
			raise KeyError(key)

		# Delete item from index
		with self.index.modify() as index:
			if key in index:
				index.remove(key)

		# Delete item from filesystem
		remove(self.objects.read(key))

	def __iter__(self):
		for key in self.index.read():
			yield key
		
	def keys(self):
		for key in self:
			yield key

	def values(self):
		for key in self:
			yield self[key]

	def items(self):
		for key in self:
			yield key, self[key]

	def get(self, key):
		if key in self:
			return self[key]

	def pop(self, key, default=None):
		# TODO: fix default variable
		try:
			value = self[key]
			del self[key]
			return value
		except KeyError:
			if default is not None:
				return default
			raise

	def popitem(self):
		key = self.keys().pop()
		return key, self.pop(key)

	def copy(self):
		return Bunch(
			[
				# Deep copy any other instances
				(key, value) if not isinstance(value, self.__class__) else (key, value.copy())
				# For all items in self
				for key, value in self.items()
			]
		)

	def clear(self):
		for key in self:
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

	def __repr__(self):
		return "{%s}" % ", ".join("%r: %r" % item for item in self.items())