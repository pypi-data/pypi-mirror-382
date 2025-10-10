"""Anything that has a classmethod to create an argument parser"""

# imports
from abc import ABC, abstractmethod
from argparse import ArgumentParser


class HasArgumentParser(ABC):
    """
    Any object that has an argument parser
    """

    @classmethod
    @abstractmethod
    def get_argument_parser(cls) -> ArgumentParser:
        """
        Return the argument parser that objects of this class use.

        Not implemented in the base class
        """
        raise NotImplementedError
