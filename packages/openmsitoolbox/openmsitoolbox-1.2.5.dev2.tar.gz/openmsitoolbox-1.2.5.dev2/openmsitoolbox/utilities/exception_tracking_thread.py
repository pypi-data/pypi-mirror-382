" A Thread that re-raises any Exceptions encountered during running when it is join()ed "

# imports
from threading import Thread


class ExceptionTrackingThread(Thread):
    """
    A Thread that will keep track of any exceptions thrown and raise them when join()
    is called
    """

    @property
    def caught_exception(self) -> Exception:
        """
        Any Exception encountered while the thread is running
        """
        return self.__exc

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__exc = None

    def run(self, *args, **kwargs) -> None:
        """
        Wrapper around Thread.run that holds onto any Exception raised during running
        """
        try:
            super().run(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.__exc = exc

    def join(self, *args, **kwargs) -> None:
        """
        Wrapper around Thread.join that re-raises any Exceptions that were encountered
        """
        super().join(*args, **kwargs)
        if self.__exc is not None:
            raise self.__exc
