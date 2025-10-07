import logging
import sys

# Define the log format (with milliseconds) and date format
LOG_FORMAT  = "%(asctime)s.%(msecs)03d %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create a formatter
_formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

# Create a stream handler (to stdout) and attach the formatter
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_formatter)

# Get your “dai” logger
dai_logger = logging.getLogger("digital_ai")
dai_logger.setLevel(logging.DEBUG)
dai_logger.propagate = False
if not dai_logger.handlers:
    dai_logger.addHandler(_handler)
