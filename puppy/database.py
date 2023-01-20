import os
import json
import hashlib
import threading
import contextlib

from puppy.bunch import Bunch


class Database(object):

	def __init__(self, path):
		# Store path information
		self.path = path
		self.index = os.path.join(path, "index")
		self.objects = os.path.join(path, "objects")

		# Store thread-safeing variables
		self.lock = threading.Lock()

		# Make sure objects path exists
		if not os.path.exists(self.objects):
			os.makedirs(self.objects)

	def _read(self):
		# Make sure index exists
		if not os.path.exists(self.index):
			return list()

		# Read index contents
		with open(self.index, "r") as file:
			return json.load(file)

	@contextlib.contextmanager
	def _modify(self):
		# Lock the mutex
		with self.lock:
			# Read the index
			index = self._read()

			# Yield the index for modification
			yield index

			# Write index contents
			with open(self.index, "w") as file:
				json.dump(index, file)

	def _object(self, key):
		return os.path.join(self.objects, hashlib.sha256(key.encode()).hexdigest())

	def __contains__(self, key):
		# Make sure file exists
		if not os.path.exists(self._object(key)):
			return False
		
		# Make sure index contains key
		return key in iter(self)

	def __getitem__(self, key):
		# Make sure key exists
		assert key in self, "No such key"

		# Read file contents
		with open(self._object(key), "r") as file:
			value = json.load(file)

		# Check if value is a dictionary
		if not isinstance(value, dict):
			return value

		# Convert value to bunch and return
		return Bunch(value)

	def __setitem__(self, key, value):
		# Make sure value is JSON seriallizable
		json.dumps(value)

		# Check if key needs to be added to index
		if key not in self:
			with self._modify() as index:
				if key not in index:
					index.append(key)

		# Write string value to file
		with open(self._object(key), "w") as file:
			json.dump(value, file)

	def __delitem__(self, key):
		# Make sure key exists
		assert key in self, "No such key"

		# Delete item from index
		with self._modify() as index:
			if key in index:
				index.remove(key)

		# Delete item from filesystem
		os.remove(self._object(key))

	def __iter__(self):
		for key in self._read():
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

	def __repr__(self):
		return "%s(%r)" % (self.__class__.__name__, self.path)
