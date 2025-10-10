" OpenMSI logging formatter "

# imports
import logging


class OpenMSIFormatter(logging.Formatter):
    """
    Very small extension of the usual logging.Formatter to allow modification of format
    based on message content
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        """
        If a message starts with a newline, start the actual logging line with the newline
        before any of the rest
        """
        formatted = ""
        if record.msg.startswith("\n"):
            record.msg = record.msg.lstrip("\n")
            formatted += "\n"
        formatted += super().format(record)
        return formatted
