" Anything that owns an OpenMSILogger "

# imports
from argparse import Namespace
import logging
import pathlib
from typing import Any, Dict, List, Tuple
from ..argument_parsing.has_arguments import HasArguments
from .openmsi_logger import OpenMSILogger


class LogOwner(HasArguments):
    """
    Any subclasses extending this one will have access to a Logger defined by
    the first class in the MRO to extend it

    :param logger: a :class:`OpenMSIToolbox.logging.OpenMSILogger` object that this class
        should have access to. If this parameter is given it will override any of the
        others provided.
    :type logger: :class:`OpenMSIToolbox.logging.OpenMSILogger`, optional
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
    """

    @property
    def logger(self):
        """
        The logger object that the class can use
        """
        return self.__logger

    @logger.setter
    def logger(self, logger: OpenMSILogger) -> None:
        if (
            hasattr(self, "_LogOwner__logger")
            and self.__logger is not None
            and (not isinstance(self.__logger, type(logger)))
        ):
            errmsg = (
                f"ERROR: tried to reset a logger of type {type(self.__logger)} "
                f"to a new logger of type {logger}!"
            )
            self.__logger.error(errmsg, exc_type=ValueError)
        else:
            self.__logger = logger

    def __init__(
        self,
        *args,
        logger: OpenMSILogger = None,
        logger_name: str = None,
        streamlevel: int = logging.INFO,
        logger_file: pathlib.Path = None,
        filelevel: int = logging.WARNING,
        **other_kwargs,
    ) -> None:
        if logger is not None:
            self.__logger = logger
        else:
            if logger_name is None:
                logger_name = self.__class__.__name__
            logger_filepath = logger_file
            if logger_file is not None and logger_file.is_dir():
                logger_filepath = logger_file / f"{logger_name}.log"
            self.__logger = OpenMSILogger(
                logger_name, streamlevel, logger_filepath, filelevel
            )
        super().__init__(*args, **other_kwargs)
        # super().__init__()

    @classmethod
    def get_command_line_arguments(cls) -> Tuple[List[str], Dict[str, Any]]:
        """
        Return the names of arguments for the logger stream and file levels.
        """
        superargs, superkwargs = super().get_command_line_arguments()
        args = [
            *superargs,
            "logger_stream_level",
            "logger_file_path",
            "logger_file_level",
        ]
        return args, superkwargs

    @classmethod
    def get_init_args_kwargs(
        cls, parsed_args: Namespace
    ) -> Tuple[List[str], Dict[str, Any]]:
        superargs, superkwargs = super().get_init_args_kwargs(parsed_args)
        kwargs = {
            **superkwargs,
            "streamlevel": parsed_args.logger_stream_level,
            "logger_file": parsed_args.logger_file_path,
            "filelevel": parsed_args.logger_file_level,
        }
        return superargs, kwargs
