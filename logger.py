import logging

logger_initialized = False

def setup_logger(file_name):
    """
    Sets up a logger that writes to a single log file.
    """
    
    global logger_initialized

    file_mode = 'w' if not logger_initialized else 'a'  # Write mode for the first call, append mode later
    
    logging.basicConfig(
        filename = f"{file_name}.log",
        level = logging.INFO,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filemode=file_mode,
    )
    logger_initialized = True  # Set the flag to True after the first call
    
    return logging.getLogger()
