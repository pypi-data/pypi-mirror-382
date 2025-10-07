import threading
import platform
import time
import inspect
import copy
import json
from datetime import datetime

from thalabus.utils import get_os_type

LOG_FILENAME = "thalabus.log"
LOG_PLAN_FILENAME = "plan.log"
ENABLE_LOG_SCREEN_LOCK = True
MAX_DEBUG_MESSAGES = 12

DEBUG    = 0
LLM_IN   = 1
LLM_OUT  = 2
FUNCTION = 3
INFO     = 4
PLAN     = 5
WARNING  = 6
ERROR    = 7
FATAL    = 8
Level_Strings = ["DEBUG", "LLM_IN", "LLM_OUT", "FUNCTION", "INFO", "PLAN", "WARNING", "ERROR", "FATAL"]

# Log globals
LogFile = None
LogLock = threading.Lock()
LogThread = None
Debug_messages = []

# ANSI color codes for console output
RESET = "\033[0m"
GRAY = "\033[90m"
WHITE = "\033[97m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
LIGHT_GRAY = "\033[37m"
DARK_GRAY = "\033[90m"
LIGHT_RED = "\033[91m"
LIGHT_GREEN = "\033[92m"
LIGHT_YELLOW = "\033[93m"
LIGHT_BLUE = "\033[94m"
LIGHT_MAGENTA = "\033[95m"
LIGHT_CYAN = "\033[96m"
C_NEUTRAL = GRAY
C_DEBUG = GRAY
C_LLM_IN = MAGENTA
C_LLM_OUT = BLUE
C_FUNCTION = GREEN
C_INFO = WHITE
C_PLAN = BLACK
C_WARNING = YELLOW
C_ERROR = RED
C_FATAL = LIGHT_RED
C_LEVEL_CODES = [C_DEBUG, C_LLM_IN, C_LLM_OUT, C_FUNCTION, C_INFO, C_PLAN, C_WARNING, C_ERROR, C_FATAL]

# Multithreading locks to enable thread-safe execution
print_lock = threading.Lock()

# console output configuration
console_log_level = None

def log_thread():
    global LogFile
    while LogFile:
        # every 2 seconds, flush the log file
        with LogLock:
            if LogFile:
                LogFile.flush()
        time.sleep(2)
    return

def log_init(log_filename:str=LOG_FILENAME, disable_screen_lock:bool=False, limit_console_log_level:int=None):
    global LogFile, LogThread, console_log_level
    if LogFile:
        return
    
    os_type = get_os_type()
    if os_type == "Linux":
        base_path = "/app/"
    else:
        base_path = "./"

    if disable_screen_lock:
        global ENABLE_LOG_SCREEN_LOCK
        ENABLE_LOG_SCREEN_LOCK = False
    
    if limit_console_log_level is not None:
        console_log_level = limit_console_log_level

    if LogFile:
        LogFile.close()
    LogFile = open(base_path + log_filename, "w", encoding="utf-8")

    if LogThread is None:
        LogThread = threading.Thread(target=log_thread)
        LogThread.start()
    return

def log_exit():
    global LogFile, LogThread
    with LogLock:
        if LogFile:
            LogFile.flush()
            LogFile.close()
            LogFile = None

        if LogThread:
            LogThread.join()
            LogThread = None
    return

def find_class_in_stack_frame(stack):
    for frame in stack:
        if "self" in frame.frame.f_locals:
            return frame.frame.f_locals["self"]
    return None

def find_goal_in_stack_frame(stack):
    for frame in stack:
        if "goal" in frame.frame.f_locals:
            return frame.frame.f_locals["goal"]
    c = find_class_in_stack_frame(stack)
    if c and c.__class__.__name__ == "Goal":
        return c
    return None

def find_session_id_in_stack_frame(stack) -> str:
    for frame in stack:
        c = frame.frame.f_locals.get("self", None)
        if c:
            if c.__class__.__name__ == "RemoteSession":
                if hasattr(c, "rs_session") and c.rs_session is not None:
                    return c.rs_session.s_id
            elif c.__class__.__name__ == "Session":
                if hasattr(c, "s_id"):
                    return c.s_id
        else:
            locals = frame.frame.f_locals
            for key, value in locals.items():
                if value.__class__.__name__ == "RemoteSession" and value.rs_session is not None:
                    return value.rs_session.s_id
    return None

def process_newlines(obj):
    if isinstance(obj, dict):
        return {k: process_newlines(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [process_newlines(elem) for elem in obj]
    elif isinstance(obj, str):
        replaced = obj.replace('\\n', '\n')
        return replaced
    else:
        return obj

def log(level:int, msg:str):
    global LogFile, Level_Strings, Debug_messages, console_log_level

    # Get the calling frame
    stack = inspect.stack()

    # Option to set breakpoints here
    if level >= WARNING:
        pass
    if level >= ERROR:
        pass

    # Get the calling function name
    os_type = platform.system()
    separator = "\\" if os_type == "Windows" else "/"
    calling_function_name = {msg.split("'")[1]} if level==FUNCTION and "'" in msg else ""
    calling_function = stack[1].function + f"({calling_function_name})"
    calling_module = stack[1].filename.split(separator)[-1]
    calling_class = find_class_in_stack_frame(stack)
    calling_class_name = calling_class.__class__.__name__ if calling_class else ""
    calling_goal = find_goal_in_stack_frame(stack)
    calling_session = find_session_id_in_stack_frame(stack)
    if calling_goal:
        calling_goal_id = calling_goal.get_id_chain_as_str()
    elif calling_session:
        calling_goal_id = calling_session
    else:
        calling_goal_id = ""

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg_color = C_LEVEL_CODES[level]

    # format the message content
    if isinstance(msg, dict) or isinstance(msg, list):
        # pretty print the dictionary or list, with indentation, spaces, and newlines
        msg_copy = copy.deepcopy(msg)
        msg_copy = process_newlines(msg_copy)
        msg_formatted = json.dumps(msg_copy, indent=4, separators=(',', ': '))
        msg_formatted = msg_formatted.replace('\\n', '\n')
    elif level == PLAN:
        # pretty print the plan
        msg_formatted = msg.__str__()
    else:
        msg_formatted = msg

    # format the log message
    calling_module = calling_module[:20]
    calling_class_name = calling_class_name[:20]
    calling_goal_id = calling_goal_id[:15]
    calling_function = calling_function[:30]
    color_class = C_NEUTRAL if level not in [LLM_IN, LLM_OUT] else msg_color
    color_function = C_NEUTRAL if level not in [FUNCTION] else msg_color
    log_message_file = f"{C_NEUTRAL}{timestamp}|{calling_module:<20}|{color_class}{calling_class_name:<20}{C_NEUTRAL}|{calling_goal_id:<15}|{color_function}{calling_function:<30}{RESET}|{msg_color}{Level_Strings[level]:<8}{RESET}|{msg_color}{msg_formatted}{RESET}"
    if os_type == "Linux":
        if isinstance(msg, dict) or isinstance(msg, list):
            # no formatting with Blazor debug pages
            msg_console = json.dumps(msg)
        else:
            # formatting without ANSI terminal colors when debugging on Linux
            msg_console = msg_formatted.replace('\n', '\\n')
        log_message_console = f"{timestamp}|{calling_module:<20}|{calling_class_name:<20}|{calling_goal_id:<15}|{calling_function:<30}|{Level_Strings[level]:<8}|{msg_console}"
    else:
        # formatting for ANSI terminal colors when debugging on Windows or Macintosh
        log_message_console = log_message_file

    # print to console, which requires a lock to prevent interleaving among multiple threads
    if console_log_level is None or level >= console_log_level:
        with print_lock:
            if ENABLE_LOG_SCREEN_LOCK and level == DEBUG:
                log_message_console = log_message_console.replace("\n", "  |||  ")
                if len(Debug_messages) < MAX_DEBUG_MESSAGES:
                    # Add the debug message to the list of debug messages
                    Debug_messages.append(log_message_console)
                    print(log_message_console)
                else:
                    # Move the cursor up 10 rows + clear the screen from the cursor down + reprint the debug messages
                    Debug_messages.pop(0)
                    Debug_messages.append(log_message_console)
                    print(f"\033[{MAX_DEBUG_MESSAGES}A\033[J" + "\n".join(Debug_messages))
            else:
                if len(Debug_messages) > 0:
                    # Clear all debug messages and print the current message
                    print(f"\033[{len(Debug_messages)}A\033[J" + log_message_console)
                    Debug_messages = []
                else:
                    print(log_message_console)

    # write the log message to the log file
    with LogLock:
        if not LogFile:
            log_init()

        LogFile.write(f"{log_message_file}\n")
        if os_type != "Linux" or level >= WARNING:
            LogFile.flush()
    return

# logs the thalabus plan to "plan.log"
def log_plan(plan) -> None:
    try:
        # update the plan log
        plan_str = plan.__str__()
        with open(LOG_PLAN_FILENAME, "w", encoding="utf-8") as f:
            f.write(f"Plan log: {datetime.now()}\n\n")
            f.write(plan_str)
            f.write("\n")
    except Exception as e:
        log(ERROR, f"Error writing plan log: {e}")

    return


if __name__ == "__main__":
    log_init()
    log(INFO, "Start of normal logging test")
    log(DEBUG, "Debug message")
    log(LLM_IN, "LLM messages")
    log(LLM_OUT, "LLM responses")
    log(FUNCTION, "Function message")
    log(INFO, "Info message")
    log(WARNING, "Warning message")
    log(ERROR, "Error message")
    log(FATAL, "Fatal message")

    log(INFO, "Start of ANSI SCREEN LOCK feature test")
    for i in range(5):
        log(DEBUG, f"Message {i}")
        time.sleep(0.25)

    log(INFO, "Start of second ANSI SCREEN LOCK feature test\nThis message is very long to test the screen lock feature\nIt is so long that it will be split into multiple lines")

    for i in range(5):
        log(DEBUG, f"Message {i}")
        time.sleep(0.25)

    log(INFO, "Start of third ANSI SCREEN LOCK feature test")
    for i in range(20):
        log(DEBUG, f"Message {i}")
        time.sleep(0.25)
        if i==5:
            log(DEBUG, "VERY LONG DEBUGGING MESSAGE\nIN MULTIPLE LINES\nTO TEST THE SCREEN LOCK FEATURE")
            time.sleep(1)
    log(INFO, "End of ANSI SCREEN LOCK feature test")

    log_exit()
