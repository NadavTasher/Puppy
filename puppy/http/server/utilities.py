import ssl  # NOQA
import contextlib  # NOQA

SUPPRESSED_MESSAGES = ["ALERT_CERTIFICATE_UNKNOWN"]


@contextlib.contextmanager
def supress_certificate_errors():
    try:
        # Yield for execution
        yield
    except ssl.SSLError as exception:
        # Check if message should be ignored
        if not any(message in str(exception) for message in SUPPRESSED_MESSAGES):
            raise
