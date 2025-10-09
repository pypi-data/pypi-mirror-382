import logging
from os import environ
from pathlib import Path

from colorlog import ColoredFormatter

from .time import local_time

__all__ = ['logger', 'init_filelogger']


class DistributedLogger(logging.RootLogger):

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO) and environ.get('RANK', '0') == '0':
            self._log(logging.INFO, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG) and environ.get('RANK', '0') == '0':
            self._log(logging.DEBUG, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING) and environ.get('RANK', '0') == '0':
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR) and environ.get('RANK', '0') == '0':
            self._log(logging.ERROR, msg, args, **kwargs)


logger = DistributedLogger(logging.WARNING)

log_format = '[%(levelname)s >> %(asctime)s file %(filename)s, function %(funcName)s, line %(lineno)d]: %(message)s'

if not logger.hasHandlers():
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(ColoredFormatter('%(log_color)s' + log_format, reset=True))
    logger.addHandler(handler)


def init_filelogger(
    name: str = "default",
    logdir: str = '/tmp/log',
    log_level: str = 'DEBUG'
) -> bool:
    _logdir = logdir if isinstance(logdir, Path) else Path(logdir)
    logname = _logdir / f'{name}_{local_time()}.log'

    if environ.get('RANK', '0') != '0' or (
        len(logger.handlers) == 2 and logger.handlers[1].baseFilename == logname):
        return False

    logger.handlers[0].setLevel(getattr(logging, log_level))

    _logdir.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(logname)
    handler.setFormatter(logging.Formatter(log_format))
    handler.setLevel(logging.DEBUG)

    if len(logger.handlers) == 1:
        logger.addHandler(handler)
    else:
        logger.handlers[1] = handler
    logger.info(f'{name} logger initialized, log file saved to {logname}')

    return True
