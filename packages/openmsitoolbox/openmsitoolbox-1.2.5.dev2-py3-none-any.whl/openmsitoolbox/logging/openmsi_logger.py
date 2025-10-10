" OpenMSI-configured logger "

# imports
import logging
import warnings
import pathlib
from typing import Type
from .formatter import OpenMSIFormatter


class OpenMSILogger:
    """
    A general logger in OpenMSI format.

    :param logger_name: The name for the logger to use
        (automatically inferred from the running module if not given)
    :type logger_name: str, optional
    :param streamlevel: The level at/above which messages should be logged to the stream/console
    :type streamlevel: logging level int, optional
    :param logger_filepath: The path to a logger file to use or directory in which
        an automatically-named logger file should be created
    :type logger_filepath: :class:`pathlib.Path`, optional
    :param filelevel: The level at/above which messages should be written to the logfile
    :type filelevel: logging level int, optional
    :param conf_global_logger: Whether to configure global loggers or not (Default: True)
    :type conf_global_logger: bool, optional
    """

    FORMATTER = OpenMSIFormatter(
        "[%(name)s %(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    level = logging.NOTSET

    def __init__(
        self,
        logger_name: str = None,
        streamlevel: int = logging.INFO,
        logger_filepath: pathlib.Path = None,
        filelevel: str = logging.WARNING,
        conf_global_logger: bool = True,
    ) -> None:
        """
        name = the name for this logger to use (probably something like the top module that owns it)
        """
        # set global logging level if requested. We use the lower number (more verbose) as default
        self.level = min(streamlevel, filelevel)
        if conf_global_logger:
            # This line ensures a default level if logger hasnt yet been used
            logging.basicConfig(level=self.level)
            # This line ensures a default level on the root logger if logger has been used
            logging.getLogger().setLevel(self.level)
        self._name = logger_name
        if self._name is None:
            self._name = self.__class__.__name__
        self._logger_obj = logging.getLogger(self._name)
        self._logger_obj.setLevel(logging.DEBUG)
        self._streamhandler = logging.StreamHandler()
        self._streamhandler.setLevel(streamlevel)
        self._streamhandler.setFormatter(self.FORMATTER)
        self._logger_obj.addHandler(self._streamhandler)
        self._filehandler = None
        if logger_filepath is not None:
            self.add_file_handler(logger_filepath, level=filelevel)
        if conf_global_logger:
            # override warnings output via us
            warnings.showwarning = lambda message, category, filename, lineno, f=None, line=None: self._logger_obj.warning(
                warnings.formatwarning(message, category, filename, lineno)
            )

    def set_level(self, level: int) -> None:
        """
        Set the level of the entire underlying logger

        :param level: The level to set
        :type level: logging level int
        """
        self._logger_obj.setLevel(level)

    def set_stream_level(self, level: int) -> None:
        """
        Set the level of the underlying logger's streamhandler

        :param level: The level to set
        :type level: logging level int
        """
        self._streamhandler.setLevel(level)

    def get_stream_level(self) -> int:
        """
        Get the current level of the underlying logger's streamhandler

        :return: The integer level of the current streamhandler
        """
        return self._streamhandler.level

    def set_file_level(self, level: int) -> None:
        """
        Set the level of the underlying logger's filehandler

        :param level: The level to set
        :type level: logging level int
        """
        if self._filehandler is None:
            errmsg = (
                f"ERROR: Logger {self._name} does not have a filehandler set "
                "but set_file_level was called!"
            )
            raise RuntimeError(errmsg)
        self._filehandler.setLevel(level)

    def add_file_handler(
        self, filepath: pathlib.Path, level: int = logging.INFO
    ) -> None:
        """
        Add an additional :class:`logging.FileHandler` to the logger

        :param filepath: The path to the new logger file
        :type filepath: :class:`pathlib.Path`
        :param level: The level to set
        :type level: logging level int
        """
        if not isinstance(filepath, pathlib.PurePath):
            self.error(
                f"ERROR: {filepath} is a {type(filepath)} object, not a Path object!",
                exc_type=TypeError,
            )
        if not filepath.is_file():
            if not filepath.parent.is_dir():
                filepath.parent.mkdir(parents=True)
            filepath.touch()
        self._filehandler = logging.FileHandler(filepath)
        self._filehandler.setLevel(level)
        self._filehandler.setFormatter(self.FORMATTER)
        self._logger_obj.addHandler(self._filehandler)

    # methods for logging different levels of messages

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message at DEBUG level. Additional args/kwargs are sent to
        the underlying logger object's debug call.

        :param msg: the message to log
        :type msg: str
        """
        self._logger_obj.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message at INFO level. Additional args/kwargs are sent to
        the underlying logger object's info call.

        :param msg: the message to log
        :type msg: str
        """
        self._logger_obj.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message at WARNING level. Additional args/kwargs are sent to
        the underlying logger object's warning call.

        :param msg: the message to log (will have "WARNING: " prepended if it doesn't start with it)
        :type msg: str
        """
        if not msg.startswith("WARNING:"):
            msg = f"WARNING: {msg}"
        self._logger_obj.warning(msg, *args, **kwargs)

    def error(
        self,
        msg: str,
        *,
        exc_type: Type[Exception] = None,
        reraise: bool = False,
        **kwargs,
    ) -> None:
        """
        Log a message at ERROR level. Optionally raise an exception of a given type
        with the same message, or re-raise an Exception object passed through the
        `exc_info` kwarg (after logging its traceback).

        Additional kwargs are sent to the underlying logger object's error call.

        :param msg: the message to log
        :type msg: str
        :param exc_type: The type of Exception to raise with the same message as `msg`
        :type exc_type: :class:`Exception`, optional
        :param reraise: if True, any :class:`Exception` object passed through the `exc_info`
            will be re-raised after its traceback is logged.
        :type reraise: bool, optional
        """
        if not msg.startswith("ERROR:"):
            msg = f"ERROR: {msg}"
        self._logger_obj.error(msg, **kwargs)
        if (
            reraise
            and ("exc_info" in kwargs)
            and isinstance(kwargs["exc_info"], Exception)
        ):
            raise kwargs["exc_info"]
        if exc_type is not None:
            raise exc_type(msg)
