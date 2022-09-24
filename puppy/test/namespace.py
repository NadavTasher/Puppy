class Namespace(dict):
	def __init__(self, values=None, **kwargs):
		# Set the converted attribute
		self._converted_ = bool(values)

		# Initialize the dictionary
		dict.__init__(self, values or {})

		# Update additional values
		for key, value in kwargs.items():
			dict.__setitem__(self, key, value)

	def __contains__(self, key):
		# Fetch the value
		value = self.__getitem__(key)

		# Check if the item is a magic
		if not isinstance(value, magic):
			return True

		# Check if the item is a valid magic
		if value:
			return True

		# Item does not exist
		return False

	def __getitem__(self, key):
		# Set default value
		if dict.__contains__(self, key):
			# Fetch value
			value = dict.__getitem__(self, key)

			# Check if value is a dict
			if type(value) == dict:
				# Convert to magic
				value = magic(value)

				# Update value
				dict.__setitem__(self, key, value)
		else:
			# Create new magic value
			value = magic()

			# Update the item
			dict.__setitem__(self, key, value)
		
		# Return value
		return value

	def __setattr__(self, key, value):
		return self.__setitem__(key, value)

	def __getattr__(self, key):
		return self.__getitem__(key)

	def __delattr__(self, key):
		return self.__delitem__(key)

	def __hasattr__(self, key):
		return self.__hasitem__(key)

	def __len__(self):
		# Initialize count
		count = 0
		
		# Count all values that are not magics or valid magics
		for key, value in self.items():
			# Skip internal items
			if key.startswith("_") and key.endswith("_"):
				continue
			
			# Make sure the value is not a magic or a valid one
			if (not isinstance(value, magic)) or bool(value):
				count += 1
		
		# Return item count
		return count

	def __bool__(self):
		# Make sure the length is not 0 or that the magic is converted
		return len(self) > 0 or self._converted_
