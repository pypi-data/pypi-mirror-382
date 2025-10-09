import time
from functools import wraps
import logging

def time_it(func):
    @wraps(func)  
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter() 
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result
    return wrapper

def setup_logging(name: str, level=logging.INFO) -> logging.Logger:
    """Configures and returns a logger instance for an application. 
    It ensures that logs from this specific logger do not interfere with other loggers.
    Formats the output to include the timestamp, logger name, log level, and the message itself."""
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent logs from bubbling up to root

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger

def enforce_type(value, expected_types, arg_name):
    """Ensure the input is the expected type"""
    if not isinstance(value, expected_types):
        expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
        expected_str = ", ".join(expected_names)
        raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")