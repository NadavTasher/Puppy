import logging  # NOQA


def setup(name="puppy", size=1024 * 1024):
    # Get default logger
    logging.basicConfig(
        filename="%s.log" % name,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        level=logging.INFO,
    )
