"""Logging utilities."""

from __future__ import annotations

import logging
import sys

from colorama import Fore, Style


# ------------------------------------------------------------------------------
def get_log_level(s: str) -> int:
    """
    Convert the string version of a log level  to the corresponding log level.

    :param s:       A string version of a log level (e.g. 'error', 'info').
                    Case is not significant.

    :return:        The numeric logLevel equivalent.

    :raises ValueError: If the supplied string cannot be converted.
    """

    if not s or not isinstance(s, str):
        raise ValueError(f'Bad log level: {s}')

    t = s.upper()

    if not hasattr(logging, t):
        raise ValueError(f'Bad log level: {s}')

    return getattr(logging, t)


# ------------------------------------------------------------------------------
class ColourLogHandler(logging.Handler):
    """Basic stream handler that writes to stderr with colours for message levels."""

    # --------------------------------------------------------------------------
    def __init__(self, colour=True):
        """Allow colour to be enabled or disabled."""

        super().__init__()
        self.colour = colour

    # --------------------------------------------------------------------------
    def emit(self, record: logging.LogRecord):
        """Print the record to stderr with some colour enhancement."""

        if self.colour:
            if record.levelno >= logging.ERROR:
                colour = Style.BRIGHT + Fore.RED
            elif record.levelno >= logging.WARNING:
                colour = Fore.MAGENTA
            elif record.levelno >= logging.INFO:
                colour = Fore.BLACK
            else:
                colour = Style.DIM + Fore.BLACK

            print(colour + self.format(record) + Fore.RESET + Style.RESET_ALL, file=sys.stderr)
        else:
            print(self.format(record), file=sys.stderr)
