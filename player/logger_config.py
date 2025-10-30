import logging


def get_file_logger(file_path: str, level=logging.INFO):
    """
    Creates and returns a logger that logs messages to a specified file.

    Args:
        file_path (str): The path to the log file.

    Returns:
        logging.Logger: A logger instance to write logs to the designated file.
    """

    # Definition of the log message format for file logging
    file_log_format = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(levelname)s : %(message)s",
        datefmt="%H:%M:%S",
    )

    # Creation of a file handler, in append mode
    handler = logging.FileHandler(file_path, mode="a")
    handler.setFormatter(file_log_format)

    # Logger configuration, with INFO level logging
    logger = logging.getLogger("file")
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False  # Avoids crossing logs with other loggers

    return logger


def get_console_logger(level=logging.INFO):
    """
    Creates and returns a logger that logs messages to the console (stdout).

    Returns:
        logging.Logger: A logger instance to print logs to the console.
    """

    # Definition of the log message format for console logging
    console_log_format = logging.Formatter(fmt="%(message)s")

    # Creation of a console handler
    handler = logging.StreamHandler()
    handler.setFormatter(console_log_format)

    # Logger configuration, with INFO level logging
    logger = logging.getLogger("console")
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
