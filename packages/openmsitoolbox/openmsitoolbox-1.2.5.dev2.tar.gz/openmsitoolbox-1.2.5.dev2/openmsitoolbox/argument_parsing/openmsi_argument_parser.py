"""Custom argument parser and associated functions"""

# imports
import pathlib
from argparse import ArgumentParser, Action
from typing import Any, Dict, List, Tuple, Type, TYPE_CHECKING
from .parser_callbacks import (
    logger_string_to_level,
    existing_file,
    create_dir,
    positive_int,
)

if TYPE_CHECKING:
    from ..runnable.runnable import Runnable


class OpenMSIArgumentParser(ArgumentParser):
    """
    An ArgumentParser with some commonly-used arguments in it.

    All constructor arguments get passed to the underlying :class:`argparse.ArgumentParser` object.

    Arguments for the parser are defined in the :attr:`~OpenMSIArgumentParser.ARGUMENTS`
    class variable, which is a dictionary. The keys are names of arguments, and the values
    are lists. The first entry in each list is a string reading "positional" or "optional"
    depending on the type of argument, and the second entry is a dictionary of keyword arguments
    to send to :func:`argparse.ArgumentParser.add_argument`.
    """

    DEF_UPDATE_SECS = 300  # default update seconds

    ARGUMENTS = {
        "logger_stream_level": [
            "optional",
            {
                "type": logger_string_to_level,
                "default": "info",
                "help": (
                    "Messages below this level will not be processed "
                    "by the logger's stream handler"
                ),
            },
        ],
        "logger_file_level": [
            "optional",
            {
                "type": logger_string_to_level,
                "default": "warning",
                "help": (
                    "Messages below this level will not be processed by the logger's file handler"
                ),
            },
        ],
        "logger_file_path": [
            "optional",
            {
                "type": pathlib.Path,
                "help": "A path to an alternate log file (instead of various defaults).",
            },
        ],
        "filepath": [
            "positional",
            {"type": existing_file, "help": "Path to the file to use"},
        ],
        "output_dir": [
            "positional",
            {"type": create_dir, "help": "Path to the directory to put output in"},
        ],
        "n_threads": [
            "optional",
            {
                "type": positive_int,
                "help": "Maximum number of threads to use",
            },
        ],
        "update_seconds": [
            "optional",
            {
                "default": DEF_UPDATE_SECS,
                "type": int,
                "help": (
                    'Number of seconds between printing a "." to the console '
                    "to indicate the program is alive"
                ),
            },
        ],
        "optional_output_dir": [
            "optional",
            {"type": create_dir, "help": "Optional path to directory to put output in"},
        ],
        "service_name": [
            "positional",
            {"help": "The name of the service to work with"},
        ],
        "optional_service_name": [
            "optional",
            {
                "help": (
                    "The customized name of the Service that will be installed "
                    "to run the chosen class"
                )
            },
        ],
        "run_mode": [
            "positional",
            {
                "choices": [
                    "start",
                    "status",
                    "stop",
                    "remove",
                    "stop_and_remove",
                    "reinstall",
                    "stop_and_reinstall",
                    "stop_and_restart",
                ],
                "help": "What to do with the service",
            },
        ],
        "remove_env_vars": [
            "optional",
            {
                "action": "store_true",
                "help": (
                    "Add this flag to also remove username/password environment variables"
                    "when removing a Service"
                ),
            },
        ],
        "remove_install_args": [
            "optional",
            {
                "action": "store_true",
                "help": (
                    "Add this flag to also remove the install arguments file "
                    "when removing a Service"
                ),
            },
        ],
        "remove_nssm": [
            "optional",
            {
                "action": "store_true",
                "help": "Add this flag to also remove the NSSM executable when removing a Service",
            },
        ],
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__argnames_added = []
        self.__subparsers_action_obj = None
        self.__subparsers = {}
        self.__subparser_argnames_added = {}

    def add_subparsers(self, *args, **kwargs):
        """
        Overloaded from base class; OpenMSIArgumentParser actually owns its subparsers
        to simplify conflicting argument names
        """
        if self.__subparsers_action_obj is not None or self.__subparsers:
            raise RuntimeError(
                "ERROR: add_subparsers called for an argument parser that already has subparsers!"
            )
        self.__subparsers_action_obj = super().add_subparsers(*args, **kwargs)

    def parse_args(self, *args, **kwargs):
        """
        Overloaded from base class to print usage when catching errors in parsing arguments
        """
        try:
            return super().parse_args(*args, **kwargs)
        except Exception:
            self.print_usage()
            raise

    #################### UNIQUE FUNCTIONS ####################

    def add_arguments(self, *args, **kwargs) -> None:
        """
        Add a group of common arguments to the parser

        :param args: Names of arguments that should be added exactly as they're listed in
            :attr:`~OpenMSIArgumentParser.ARGUMENTS`
        :type args: list
        :param kwargs: Dictionary whose keys are argument names like in `args` and
            whose values are new default argument values
        :type kwargs: dict

        :raises ValueError: if the name of an argument isn't recognized in
            :attr:`~OpenMSIArgumentParser.ARGUMENTS`, or if the type of a new
            default argument is different than the type of its original default argument
        """
        if len(args) < 1 and len(kwargs) < 1:
            raise ValueError(
                "ERROR: must specify at least one desired argument to create an argument parser!"
            )
        args_to_use = []
        for argname in args:
            if argname not in args_to_use:
                args_to_use.append(argname)
        for argname in kwargs:
            if argname in args_to_use:
                args_to_use.remove(argname)
        for argname in args_to_use:
            argname_to_add, kwargs_for_arg = self.__get_argname_and_kwargs(argname)
            if argname_to_add not in self.__argnames_added:
                self.add_argument(argname_to_add, **kwargs_for_arg)
                self.__argnames_added.append(argname_to_add)
        for argname, argdefault in kwargs.items():
            argname_to_add, kwargs_for_arg = self.__get_argname_and_kwargs(
                argname, argdefault
            )
            if argname_to_add not in self.__argnames_added:
                self.add_argument(argname_to_add, **kwargs_for_arg)
                self.__argnames_added.append(argname_to_add)

    def add_subparser_arguments(
        self,
        subp_name: str,
        args_to_add: List[str] = None,
        kwargs_to_add: Dict[str, Any] = None,
        **other_kwargs,
    ) -> None:
        """
        Create a new subparser and add arguments to it.

        :param subp_name: the name of the subparser command
        :type subp_name: str
        :param args_to_add: additional arguments that should be added to the subparser
            (same format as `args` for :func:`~OpenMSIArgumentParser.add_arguments`)
        :type args_to_add: list, optional
        :param kwargs_to_add: additional keyword arguments that should be added to the subparser
            (same format as `kwargs` for :func:`~OpenMSIArgumentParser.add_arguments`)
        :type kwargs_to_add: dict, optional
        :param other_kwargs: any other keyword arguments are passed to the subparser's
            add_parser() method
        :type other_kwargs: dict, optional

        :raises ValueError: like in :func:`~OpenMSIArgumentParser.add_arguments`
        """
        if self.__subparsers_action_obj is None:
            errmsg = (
                "ERROR: add_subparser_arguments called for an argument parser "
                "that has not added subparsers!"
            )
            raise RuntimeError(errmsg)
        if subp_name in self.__subparsers:
            errmsg = (
                f"ERROR: subparser arguments for {subp_name} have already been added "
                "to this argument parser!"
            )
            raise RuntimeError(errmsg)
        self.__subparsers[subp_name] = self.__subparsers_action_obj.add_parser(
            subp_name, **other_kwargs
        )
        self.__subparser_argnames_added[subp_name] = []
        if args_to_add is not None:
            for argname in args_to_add:
                argname_to_add, kwargs_for_arg = self.__get_argname_and_kwargs(argname)
                if argname_to_add not in self.__subparser_argnames_added[subp_name]:
                    self.__subparsers[subp_name].add_argument(
                        argname_to_add, **kwargs_for_arg
                    )
                    self.__subparser_argnames_added[subp_name].append(argname_to_add)
        if kwargs_to_add is not None:
            for argname, argdefault in kwargs_to_add.items():
                argname_to_add, kwargs_for_arg = self.__get_argname_and_kwargs(
                    argname, argdefault
                )
                if argname_to_add not in self.__subparser_argnames_added[subp_name]:
                    self.__subparsers[subp_name].add_argument(
                        argname_to_add, **kwargs_for_arg
                    )
                    self.__subparser_argnames_added[subp_name].append(argname_to_add)

    def add_subparser_arguments_from_class(
        self,
        class_to_add: Type["Runnable"],
        *,
        subp_name: str = None,
        addl_args: List[str] = None,
        addl_kwargs: Dict[str, Any] = None,
        **other_kwargs,
    ) -> None:
        """
        Create a new subparser and add arguments from the given class to it.
        `class_to_add` must inherit from :class:`~Runnable` to be able to get its arguments.

        :param subp_name: an override for the name of the command the subparser
            should be registered under. (Default is the name of the class.)
        :type subp_name: str, optional
        :param addl_args: additional arguments that should be added to the subparser
            (same format as `args` for :func:`~OpenMSIArgumentParser.add_arguments`)
        :type addl_args: list, optional
        :param addl_kwargs: additional keyword arguments that should be added to the subparser
            (same format as `kwargs` for :func:`~OpenMSIArgumentParser.add_arguments`)
        :type addl_kwargs: dict, optional
        :param other_kwargs: any other keyword arguments are passed to subparsers'
            add_parser() method
        :type other_kwargs: dict, optional

        :raises ValueError: like in :func:`~OpenMSIArgumentParser.add_arguments`
        """
        if subp_name is None:
            subp_name = class_to_add.__name__
        argnames, argnames_with_defaults = class_to_add.get_command_line_arguments()
        if addl_args is not None:
            argnames = [*argnames, *addl_args]
        if addl_kwargs is not None:
            argnames_with_defaults = {**argnames_with_defaults, **addl_kwargs}
        self.add_subparser_arguments(
            subp_name, argnames, argnames_with_defaults, **other_kwargs
        )

    def __get_argname_and_kwargs(
        self, argname: str, new_default: Any = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Return the name and kwargs dict for a particular argument

        argname = the given name of the argument, will be matched to a name in ARGUMENTS
        new_default = override the default already specified in ARGUMENTS
        """
        if argname in self.ARGUMENTS:
            if self.ARGUMENTS[argname][0] == "positional":
                argname_to_add = argname
            else:
                if argname.startswith("optional_"):
                    argname_to_add = f'--{argname[len("optional_"):]}'
                else:
                    argname_to_add = f"--{argname}"
            kwargs = self.ARGUMENTS[argname][1].copy()
            if new_default is not None:
                if "default" in kwargs.keys() and not isinstance(
                    new_default, type(kwargs["default"])
                ):
                    errmsg = (
                        f"ERROR: new default value {new_default} for argument {argname} "
                        f"is of a different type than expected based on the old default "
                        f'({self.ARGUMENTS[argname]["kwargs"]["default"]})!'
                    )
                    raise ValueError(errmsg)
                kwargs["default"] = new_default
            if "default" in kwargs.keys():
                if "help" in kwargs.keys():
                    kwargs["help"] += f" (default = {kwargs['default']})"
                else:
                    kwargs["help"] = f"default = {kwargs['default']}"
            return argname_to_add, kwargs
        raise ValueError(f"ERROR: argument {argname} is not recognized as an option!")

    @property
    def actions(self) -> List[Action]:
        """
        Wrapper around parser._actions to make it publicly available
        """
        return self._actions
