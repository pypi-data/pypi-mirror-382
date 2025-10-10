# -*- coding: utf-8 -*-
"""
    RAISE Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

# ============================================
# IMPORTS
# ============================================

# Stdlib imports
from pathlib import Path
import platform
import logging
import logging.handlers

# Third-party app imports

# Imports from your apps


# ============================================
# GLOBAL CONSTANTS
# ============================================


# ============================================
# CLASSES
# ============================================

# Class for storing logging configuration
class LogConfig:
    LOGS_FOLDER_NAME = "logs"
    LOGS_FILE_NAME = "execution-logs.log"
    LOG_MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
    DEBUG = True
    LOG_PATH = (
        Path("./", LOGS_FOLDER_NAME)
        if platform.uname().system == "Linux"
        else Path(".", LOGS_FOLDER_NAME)
    )
    if not LOG_PATH.exists():
        LOG_PATH.mkdir(exist_ok=True)
    LOG_DIR = str(LOG_PATH)

    LEVEL = (
        "DEBUG" if DEBUG else "WARN"
    )  # Valid values: DEBUG | INFO | WARN | ERROR | CRITICAL
    CONSOLE_HANDLER = DEBUG
    CONSOLE_HANDLER_LEVEL = "DEBUG"
    FILE_HANDLER = True


# Class for logging
class LogClass(object):
    log_file_path = str(Path(LogConfig.LOG_DIR, LogConfig.LOGS_FILE_NAME))
    logging_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARN,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_format = "[%(levelname)s] %(asctime)s: %(message)s"
    formatter = logging.Formatter(fmt=log_format, datefmt="%d/%m/%Y %I:%M:%S %p")
    log_handlers = list()

    if LogConfig.FILE_HANDLER:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=LogConfig.LOG_MAX_FILE_SIZE, backupCount=5
        )
        file_handler.setFormatter(formatter)
        log_handlers.append(file_handler)

    if LogConfig.CONSOLE_HANDLER:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        log_handlers.append(console_handler)

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(".".join([__name__, self.__class__.__name__]))

        def add_handler_if_absent(self, handler):
            if all(
                id(handler) != id(handler_item) for handler_item in self.logger.handlers
            ):
                self.logger.addHandler(handler)

        for handler in LogClass.log_handlers:
            add_handler_if_absent(self, handler)
        self.logger.setLevel(
            LogClass.logging_levels.get(LogConfig.LEVEL.upper(), logging.WARN)
        )

    def log_debug(self, log_message):
        self.logger.debug(log_message)

    def log_info(self, log_message):
        self.logger.info(log_message)

    def log_warning(self, log_message):
        self.logger.warning(log_message)

    def log_exception(self, log_message):
        self.logger.exception(log_message)

    def log_error(self, log_message):
        self.logger.error(log_message)

    def log_critical(self, log_message):
        self.logger.critical(log_message)
