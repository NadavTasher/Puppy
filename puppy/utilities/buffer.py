# Encoding to be used
ENCODING = "utf8"

class bytebuffer(bytearray):
	def __init__(self, argument=None):
		# If argument is not defined, empty!
		if not argument:
			# Initialize an empty buffer
			super(bytebuffer, self).__init__()
			return

		# Check if argument is a string and encode
		if isinstance(argument, str):
			# Encode the argument
			argument = argument.encode(ENCODING)

		# Initialize with argument
		super(bytebuffer, self).__init__(argument)

	def __str__(self):
		# Decode the buffer
		return self.decode(ENCODING)

	def __repr__(self):
		# Format as initializable string
		return "%s(%r)" % (self.__class__.__name__, str(self))

