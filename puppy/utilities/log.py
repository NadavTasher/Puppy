import sys  # NOQA
import logging  # NOQA
import logging.handlers  # NOQA

FORMAT = logging.Formatter(
	"[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)


class LevelFilter(logging.Filter):
	def __init__(self, minimum=logging.NOTSET, maximum=logging.FATAL):
		# Set internal levels
		self.minimum = minimum
		self.maximum = maximum

	def filter(self, record):
		# Check if level is within the allowed levels
		return self.minimum <= record.levelno and record.levelno <= self.maximum


def setup(name=None, size=1024 * 1024):
	# Get root logger
	logger = logging.getLogger()

	# Create rotating log file handler
	if name:
		file_handler = logging.handlers.RotatingFileHandler(
			filename="%s.log" % name, mode="a", maxBytes=size, backupCount=1
		)
		file_handler.addFilter(LevelFilter())
		file_handler.setLevel(logging.NOTSET)
		file_handler.setFormatter(FORMAT)
		logger.addHandler(file_handler)

	# Create stdout log handler
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.addFilter(LevelFilter(logging.INFO, logging.INFO))
	stdout_handler.setLevel(logging.DEBUG)
	stdout_handler.setFormatter(FORMAT)
	logger.addHandler(stdout_handler)

	# Create stderr log handler
	stderr_handler = logging.StreamHandler(sys.stderr)
	stderr_handler.addFilter(LevelFilter(logging.WARNING, logging.CRITICAL))
	stderr_handler.setLevel(logging.DEBUG)
	stderr_handler.setFormatter(FORMAT)
	logger.addHandler(stderr_handler)
