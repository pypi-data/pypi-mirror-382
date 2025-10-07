import logging
from pathlib import Path
from typing import Union

from .singleton import Singleton
from ..fm_to_estry_types import PathLike


LOG_NAME = 'fm2estry'


class WarningLog(metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._warnings = []
        self._use_warnings = False

    def activate(self):
        """Store warnings."""
        self._use_warnings = True

    def deactivate(self):
        """Stop storing warnings.

        This is the default.
        """
        self._use_warnings = False

    def add(self, msg):
        """Add a warning to the warning list.

        :param msg:
            str - text to add to the warning list

        Warnings will only be added if _use_warning == True by calling the
        active() method.
        """
        if self._use_warnings:
            self._warnings.append(msg)

    def get_warnings(self):
        """Return a list of warning stored in the log.

        Return list - containing warning messages
        """
        return self._warnings

    def reset(self):
        """Delete all warnings stored in the list."""
        self._warnings = []


_WARNING_LOG = WarningLog()
"""Conveniance reference for use in this module.

There's no reason it can't be used elsewhere too, as it's a singleton anyway,
but it's possible cleaner for calling code to grab it themselves (i.e. using:
warning_log = WarningLog() or just WarningLog().activate()).
"""


class FmToEstryHandler(logging.Handler):
    """Handler used for CLI application so that warnings logging doesn't mess up the progress bar."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.held_records = []

    def emit(self, record):
        if record.levelno >= logging.WARNING:
            self.held_records.append(record)
        else:
            super().emit(record)

    def release_warnings(self, limit: int = -1):
        for i, record in enumerate(self.held_records):
            if limit >= 0 and i >= limit:
                break
            super().emit(record)
        self.held_records = []


class FmtoEstryStreamHandler(FmToEstryHandler, logging.StreamHandler):

    def __init__(self):
        super(FmtoEstryStreamHandler, self).__init__()


class FmToEstryFileHandler(FmToEstryHandler, logging.FileHandler):

    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super(FmToEstryFileHandler, self).__init__(filename, mode, encoding, delay)


def get_fm2estry_logger() -> logging.Logger:
    """Setup and return the standard logger used throughout the fm2estry package.

    Ensures that all loggers are prefixed with the 'fm2estry' name, to ensure that
    the logger can be easily disabled by client code if needed.
    Adds FmToEstryHandler (logging.Handler) to the logger to allow us to track logging
    events and handle other things when logging.

    To use, add the following lines to the top of any module in the library:
    from fm_to_estry.helpers import logging as fm_to_estry_logging
    logger = fm_to_estry_logging.get_fm2estry_logger()

    The logger instance can be used the same as any other standard python logger.
    """
    logger = logging.getLogger(LOG_NAME)

    # Disable the TMFHandler for now. Probably want to make separate calls for WarningLog anyway
    # logger.addHandler(FmToEstryHandler())
    return logger


def set_logging_level(
        level: Union['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'WARNING',
        log_to_file: PathLike = None) -> None:
    """Configure the default logging level for the "fm2estry" logger.

    Has no impact if the user code has configured its own logger.
    if log_to_file is a valid filepath, a filehandler will also be set up and logs will be
    written to file.

    :param level:
        str - keyword to set logging level.
    :param log_to_file:
        str - folder path at which logs should be written.
    """
    if log_to_file:
        log_file = Path(log_to_file)
        log_file = log_file.joinpath(f'{LOG_NAME}.log') if log_file.is_dir() else log_file.with_name(f'{LOG_NAME}.log')

        logger = logging.getLogger(LOG_NAME)
        if log_file.parent.exists():
            fhandler = logging.FileHandler(log_file.resolve())
            fhandler.setFormatter(logging.Formatter(
                "%(asctime)s %(module)-25s %(funcName)-25s line:%(lineno)-4d %(levelname)-8s %(message)s"))
            fhandler.mode = "a"
            fhandler.maxBytes = 51200
            fhandler.backupCount = 2
            logger.addHandler(fhandler)
            try:
                logger.warning("Added a file handler to log results to: {}".format(log_to_file))
            except PermissionError:
                raise PermissionError('Unable to write to given log folder')
        else:
            logger.warning('File path for log file handler does not exist at {}'.format(log_to_file))
            raise ValueError('File path for log file handler does not exist at {}'.format(log_to_file))

    level = level.upper()
    level = level if level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] else 'WARNING'
    logging.getLogger(LOG_NAME).setLevel(level)
