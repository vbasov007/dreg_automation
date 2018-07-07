import logging
from configurator import get_config


def init_mylogger():

    my_logger_name = get_config('logging')['file']

    my_logger = logging.getLogger(my_logger_name)

    if not my_logger.hasHandlers():

        level = get_config('logging')['level']

        my_logger.setLevel(level)

        logger_file_handler = logging.FileHandler(get_config('logging')['file'])

        logger_file_handler.setLevel(level)

        logger_console_handler = logging.StreamHandler()
        logger_console_handler.setLevel(level)

        logger_formatter = logging.Formatter(get_config('logging')['format'])
        logger_console_handler.setFormatter(logger_formatter)
        logger_file_handler.setFormatter(logger_formatter)

        my_logger.addHandler(logger_console_handler)
        my_logger.addHandler(logger_file_handler)

    return my_logger
