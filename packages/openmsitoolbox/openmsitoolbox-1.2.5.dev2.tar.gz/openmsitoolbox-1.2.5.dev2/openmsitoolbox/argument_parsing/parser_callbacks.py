" Argument parser callback functions "

# imports
import pathlib
import math
import logging


def logger_string_to_level(argval: str) -> int:
    """
    converts a given string representing a logger level to its corresponding integer
    """
    argval = argval.lower()
    if argval in ("notset", "debug", "info", "warning", "error", "critical"):
        return getattr(logging, argval.upper())
    try:
        if int(argval) >= 0:
            return int(argval)
        raise ValueError(f"ERROR: logger argument {argval} is not valid!")
    except ValueError as exc:
        raise exc


def existing_file(argstring: str) -> pathlib.Path:
    """
    convert a string or path argument into a path to a file, checking if it exists
    """
    filepath = pathlib.Path(argstring)
    if filepath.is_file():
        return filepath.resolve()
    raise FileNotFoundError(f"ERROR: file {argstring} does not exist!")


def existing_dir(argstring: str) -> pathlib.Path:
    """
    convert a string or path argument into a directory path, checking if it exists
    """
    dirpath = pathlib.Path(argstring)
    if dirpath.is_dir():
        return dirpath.resolve()
    raise FileNotFoundError(f"ERROR: directory {argstring} does not exist!")


def create_dir(argstring: str) -> pathlib.Path:
    """
    convert a string or path argument into a directory path, creating it if necessary
    """
    if argstring is None:  # Then the argument wasn't given and nothing should be done
        return None
    dirpath = pathlib.Path(argstring)
    if dirpath.is_dir():
        return dirpath.resolve()
    if dirpath.exists():
        raise RuntimeError(
            f"ERROR: directory path {argstring} exists but is not a directory!"
        )
    dirpath.mkdir(parents=True)
    return dirpath.resolve()


def int_power_of_two(argval: str) -> int:
    """
    make sure a given value is a nonzero integer power of two (or can be converted to one)
    """
    if not isinstance(argval, int):
        argval = int(argval)
    if argval <= 0 or math.ceil(math.log2(argval)) != math.floor(math.log2(argval)):
        raise ValueError(
            f"ERROR: invalid argument: {argval} must be a (nonzero) power of two!"
        )
    return argval


def positive_int(argval: str) -> int:
    """
    make sure a given value is a positive integer
    """
    argval = int(argval)
    if (not isinstance(argval, int)) or (argval < 1):
        raise ValueError(
            f"ERROR: invalid argument: {argval} must be a positive integer!"
        )
    return argval
