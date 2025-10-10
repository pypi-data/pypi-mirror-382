import logging
from rich.logging import RichHandler

def setup_logging():
    """
    Configures logging to use rich for beautiful output.
    """
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("rich")