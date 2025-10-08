import logging

from catwalk_client.common.constants import (
    CATWALK_CLIENT_LOG_HANDLER,
    CATWALK_CLIENT_LOG_NAME,
)


class CatwalkClientLoggingFormatter(logging.Formatter):
    GRAY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    fmt_more = "[%(asctime)s] [%(levelname)s] [%(name)s] (%(filename)s:%(lineno)d): %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S %z"

    FORMATS = {
        logging.DEBUG: BLUE + fmt_more + RESET,
        logging.INFO: GRAY + fmt + RESET,
        logging.WARNING: YELLOW + fmt + RESET,
        logging.ERROR: RED + fmt_more + RESET,
        logging.CRITICAL: BOLD_RED + fmt_more + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.date_fmt)
        return formatter.format(record)


def init_logger(logger_name: str = CATWALK_CLIENT_LOG_NAME):
    log = logging.getLogger(logger_name)

    if any(
        [handler.get_name() == CATWALK_CLIENT_LOG_HANDLER for handler in log.handlers]
    ):
        log.debug(f"Logger '{logger_name}' has already been initialized!")
        return log

    log_handler = logging.StreamHandler()
    log_handler.set_name(CATWALK_CLIENT_LOG_HANDLER)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(CatwalkClientLoggingFormatter())
    log.addHandler(log_handler)

    log_level = "INFO"
    log.setLevel(log_level)
    log.debug(f"Log level: {log_level}")

    return log


import logging
