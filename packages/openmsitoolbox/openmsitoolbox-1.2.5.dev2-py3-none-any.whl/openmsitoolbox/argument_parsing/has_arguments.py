"""
Anything that should have associated command line arguments when anything extending it
also extends Runnable
"""

# imports
from argparse import Namespace
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any


class HasArguments(ABC):
    """
    Anything that has OpenMSIArgumentParser-format command line arguments
    """

    @classmethod
    @abstractmethod
    def get_command_line_arguments(cls) -> Tuple[List[str], Dict[str, Any]]:
        """
        Get the list of argument names and the dictionary of argument names/default values
        to add to the argument parser

        :return: args, a list of argument names recognized by the argument parser
        :rtype: list(str)
        :return: kwargs, a dictionary of default argument values keyed by argument names
            recognized by the argument parser
        :rtype: dict
        """
        return [], {}

    @classmethod
    @abstractmethod
    def get_init_args_kwargs(
        cls, parsed_args: Namespace
    ) -> Tuple[List[str], Dict[str, Any]]:
        """Get the list of init arguments and the dictionary of init keyword arguments
        for this class given a namespace of, for example, parsed arguments.

        :param parsed_args: A namespace containing entries needed to determine the init
            args and kwargs for this class
        :type parsed_args: argparse.Namespace

        :return: A list of init args
        :return: A dictionary of init kwargs
        """
        return [], {}
