" Class for tests that use an OpenMSILogger "

# imports
import unittest
import logging
from .. import LogOwner
from ..utilities.misc import populated_kwargs


class TestWithLogger(LogOwner, unittest.TestCase):
    """
    Base class for unittest.TestCase classes that should own a logger
    By default the logger won't write to a file, and will set the stream level to ERROR
    Contains a function to overwrite the current stream level temporarily to log a
    particular message
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs = populated_kwargs(kwargs, {"streamlevel": logging.ERROR})
        super().__init__(*args, **kwargs)

    def log_at_level(self, msg: str, level: int, **kwargs) -> None:
        """
        Temporarily change the logger stream level for a single message to go through
        """
        old_level = self.logger.get_stream_level()
        self.logger.set_stream_level(level)
        levels_funcs = {
            logging.DEBUG: self.logger.debug,
            logging.INFO: self.logger.info,
            logging.WARNING: self.logger.warning,
            logging.ERROR: self.logger.error,
        }
        levels_funcs[level](msg, **kwargs)
        self.logger.set_stream_level(old_level)

    def log_at_debug(self, msg: str, **kwargs) -> None:
        """
        Log a message at debug level, temporarily changing the stream level
        """
        self.log_at_level(msg, logging.DEBUG, **kwargs)

    def log_at_info(self, msg: str, **kwargs) -> None:
        """
        Log a message at info level, temporarily changing the stream level
        """
        self.log_at_level(msg, logging.INFO, **kwargs)

    def log_at_warning(self, msg: str, **kwargs) -> None:
        """
        Log a message at warning level, temporarily changing the stream level
        """
        self.log_at_level(msg, logging.WARNING, **kwargs)

    def log_at_error(self, msg: str, **kwargs) -> None:
        """
        Log a message at error level, temporarily changing the stream level
        """
        self.log_at_level(msg, logging.ERROR, **kwargs)
