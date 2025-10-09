import time
from functools import wraps
import shutil

def enforce_type(value, expected_types, arg_name):
    """Verify type of the value to ensure it is valid type before entering functions"""
    if not isinstance(value, expected_types):
        expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
        expected_str = ", ".join(expected_names)
        raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")

#  A decorator that measures and prints the execution time of a function.
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

def colorize(text: str, color_code: str) -> str:
    """Returns a string with the specified ANSI color and a reset code."""
    return f"\033[{color_code}m{text}\033[0m"

def get_free_space_gb(path='/') -> float:
    #Defaults to the root directory ('/') which typically represents the system drive.
    try:
        disk_stats = shutil.disk_usage(path)

        # Convert bytes to gigabytes
        free_space_bytes = disk_stats.free
        free_space_gb = free_space_bytes / (1024**3)
        return free_space_gb
    except Exception as e:
        print(f"Error checking disk space: {e}")
        return None

#how to use
if __name__== "__main__":
    @time_it
    def say_hello():
        print("Hello world!")  
    say_hello()