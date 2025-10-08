import logging
import sys


def set_logging_level(level: str) -> None:
    """
    Set logging level for global loggers.
    
    :param name: Level of logging(Ex: DEBUG, INFO etc).
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO)
    )


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with the specified name and log level.
    
    :param name: Name for the logger (typically __name__).
    :return: Configured logger.
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers, if any, to avoid duplicate logs.
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create console handler and set its level.
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Create formatter and add it to the handler.
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add the handler to the logger.
    logger.addHandler(console_handler)

    # Prevent logs from propogating to root logger
    logger.propagate = False
    
    return logger
