"""
A process that will run while waiting for user input to check progress/status or shut it down
"""

# imports
from argparse import Namespace
import time
import sys
import datetime
from queue import Queue, Empty
from threading import Thread
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from ..logging.log_owner import LogOwner
from ..argument_parsing.openmsi_argument_parser import OpenMSIArgumentParser


def add_user_input(input_queue: Queue) -> None:
    """
    Listen for and add user input to a queue at one second intervals
    """
    while True:
        time.sleep(1)
        input_queue.put((sys.stdin.read(1)).strip())


class ControlledProcess(LogOwner, ABC):
    """
    A class to use when running processes that should remain active until they are
    explicitly shut down

    :param update_secs: number of seconds to wait between printing a progress character
        to the console to indicate the program is alive
    :type update_secs: int, optional
    """

    #################### PROPERTIES ####################

    @property
    def alive(self) -> bool:
        """
        Read-only boolean indicating if the process is running
        """
        return self.__alive

    #################### PUBLIC FUNCTIONS ####################

    def __init__(
        self,
        *args,
        update_secs: int = OpenMSIArgumentParser.DEF_UPDATE_SECS,
        **other_kwargs
    ) -> None:
        self.__update_secs = update_secs
        # start up a Queue that will hold the control commands
        self.control_command_queue = Queue()
        # use a daemon thread to allow a user to input control commands from the command line
        # while the process is running
        user_input_thread = Thread(
            target=add_user_input, args=(self.control_command_queue,)
        )
        user_input_thread.daemon = True
        user_input_thread.start()
        # a variable to indicate if the process has been shut down yet
        self.__alive = False
        # the last time the "still alive" character was printed
        self.__last_update = datetime.datetime.now()
        super().__init__(*args, **other_kwargs)

    def shutdown(self) -> None:
        """
        Stop the process running.
        """
        self.control_command_queue.task_done()
        self.__alive = False
        self._on_shutdown()

    #################### PRIVATE HELPER FUNCTIONS ####################

    def _print_still_alive(self) -> None:
        # print the "still alive" character
        if (
            self.__update_secs != -1
            and (datetime.datetime.now() - self.__last_update).total_seconds()
            > self.__update_secs
        ):
            self.logger.debug(".")
            self.__last_update = datetime.datetime.now()

    def _check_control_command_queue(self) -> None:
        # if anything exists in the control command queue
        try:
            cmd = self.control_command_queue.get(block=True, timeout=0.05)
        except Empty:
            cmd = None
        if cmd is not None:
            if cmd.lower() in ("q", "quit"):  # shut down the process
                self.shutdown()
            elif cmd.lower() in ("c", "check"):  # run the on_check function
                self._on_check()
            else:  # otherwise just skip this unrecognized command
                self._check_control_command_queue()

    #################### CLASS METHODS ####################

    @classmethod
    def get_command_line_arguments(cls) -> Tuple[List[str], Dict[str, Any]]:
        superargs, superkwargs = super().get_command_line_arguments()
        args = [*superargs, "update_seconds"]
        return args, superkwargs

    @classmethod
    def get_init_args_kwargs(
        cls, parsed_args: Namespace
    ) -> Tuple[List[str], Dict[str, Any]]:
        superargs, superkwargs = super().get_init_args_kwargs(parsed_args)
        kwargs = {
            **superkwargs,
            "update_secs": parsed_args.update_seconds,
        }
        return superargs, kwargs

    #################### ABSTRACT METHODS ####################

    @abstractmethod
    def run(self) -> None:
        """
        Classes extending this base class should include the logic of actually
        running the controlled process in this function, and should call super().run()
        before anything else to set some internal variables
        """
        self.__alive = True
        self.__last_update = datetime.datetime.now()

    @abstractmethod
    def _on_check(self) -> None:
        """
        This function is run when the "check" command is found in the control queue.

        Not implemented in the base class
        """
        raise NotImplementedError

    @abstractmethod
    def _on_shutdown(self) -> None:
        """
        This function is run when the process is stopped; it's called from :func:`~shutdown`.

        Not implemented in the base class
        """
        raise NotImplementedError
