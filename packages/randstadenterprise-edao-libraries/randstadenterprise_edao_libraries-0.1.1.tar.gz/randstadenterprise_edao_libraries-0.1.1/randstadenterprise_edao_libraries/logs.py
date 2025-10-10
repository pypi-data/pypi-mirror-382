# randstadenterprise_edao_libraries/logs.py
from datetime import datetime
import threading
from typing import List, Any
# Add objects import (though not used directly here, useful for type hints in other files)
from . import objects 

def get_current_time () -> datetime:
# =======================================================================
# RETURNS THE CURRENT DATETIME OBJECT
# =======================================================================
    # START def get_current_time
    """Returns the current datetime object."""
    return datetime.now()
# END def get_current_time

def log (inst_url: str, msg: str, logs_array: List[List[Any]], lock: threading.Lock, print_to_console: bool = False):
# =======================================================================
# LOGS A MESSAGE TO A SHARED ARRAY IN A THREAD-SAFE MANNER
# =======================================================================
    # START def log
    """
    Logs a message to the internal array in a thread-safe manner.
    
    :param inst_url: Instance URL for logging context.
    :param msg: The message to log.
    :param logs_array: The shared list storing all log entries.
    :param lock: The threading.Lock object for thread safety.
    :param print_to_console: Flag to print output to the console.
    :returns: None
    """
    if print_to_console:
        # START if print_to_console
        print(f"#{inst_url:<30}{msg}")
        # END if print_to_console
        
    # 1. Use the lock for thread safety when modifying the shared array
    with lock:
        # START with lock
        # Assumes log columns are ['instance', 'message', 'log_time']
        logs_array.append([inst_url, msg, get_current_time()])
        # END with lock
# END def log