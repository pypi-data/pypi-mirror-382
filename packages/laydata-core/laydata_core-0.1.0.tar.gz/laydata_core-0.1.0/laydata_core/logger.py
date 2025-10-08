import logging
import sys
from typing import Any

ROOT_LOGGER_NAME = "laydata"
_handler_initialized = False


def _setup_root_handler(level: str = "info"):
    global _handler_initialized
    if _handler_initialized:
        return
    
    root_logger = logging.getLogger(ROOT_LOGGER_NAME)
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        root_logger.setLevel(level_map.get(level.lower(), logging.INFO))
        root_logger.propagate = False
        _handler_initialized = True


class Logger:
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
    
    def set_level(self, level: str):
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        root_logger = logging.getLogger(ROOT_LOGGER_NAME)
        root_logger.setLevel(level_map.get(level.lower(), logging.INFO))
    
    def debug(self, message: str, **kwargs: Any):
        self._logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs: Any):
        self._logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs: Any):
        self._logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs: Any):
        self._logger.error(message, extra=kwargs)
    
    def exception(self, message: str, exc_info: Exception | None = None, **kwargs: Any):
        self._logger.exception(message, exc_info=exc_info, extra=kwargs)


def _init_default_logger() -> Logger:
    from laydata_core.config import config
    _setup_root_handler(config.LOG_LEVEL)
    return Logger(ROOT_LOGGER_NAME)


_default_logger = _init_default_logger()


def get_logger(name: str | None = None) -> Logger:
    if name is None:
        return _default_logger
    
    if not name.startswith(ROOT_LOGGER_NAME):
        name = f"{ROOT_LOGGER_NAME}.{name}"
    
    return Logger(name)


def set_default_level(level: str):
    _default_logger.set_level(level)


logger = _default_logger

