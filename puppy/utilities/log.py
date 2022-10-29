import logging  # NOQA


def setup(path=None):
    # Get root logger
    logging.basicConfig(
        # Basic log level
        level=logging.INFO,
        # Log line format
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        # Log file name and mode
        filename=path,
        filemode="a",
    )
