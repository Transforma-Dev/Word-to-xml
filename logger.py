import logging

def setup_logger(file_name):
    """
    Sets up a logger that writes to a single log file.
    """
    logging.basicConfig(
        filename = f"{file_name}.log",
        level = logging.INFO,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger()
