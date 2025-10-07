# thalabus SDK

thalabus is an SDK for integrating AI chatbot and copilot functionalities into your applications. It provides tools for seamless interaction with the thalabus platform.

## Installation

Install via pip:

```sh
pip install thalabus
```

## Usage
Import and use the SDK in your Python project:

```python
import thalabus
```

# Example usage
This code demonstrates how to use thalabus SDK to:
- create a chatbot conversation pool with 5 chatbots (RemoteSessionPool object)
- use the pool to extract information from all *.txt files from a directory, in a structured way

```python
import asyncio
import os
import sys
import fnmatch
import json
from typing import List
from thalabus.RemoteSession import RemoteSession, ContainerMessage
from thalabus.RemoteSessionPool import RemoteSessionPool
from thalabus.Log import log, log_init, log_exit, DEBUG, LLM_IN, LLM_OUT, FUNCTION, INFO, PLAN, WARNING, ERROR, FATAL

FOLDER = "./path/to/folder/with/articles"
PATTERN = "*.txt"

JSON_OUTPUT = {
    "title": "The main title of the publication",
    "authors": ["author1", "author2", "..."],
    "publication_date": "The online publication date in format DD.MM.YYYY",
    "journal": "The publishing journal. Normally this information is at the top or bottom of the page.",
    "abstract": "Provide a short summary of the article. Use the abstract from the first page, if provided"
}

THALABUS_PROTOCOL = "http"
THALABUS_HOSTNAME = "localhost"
THALABUS_PORT = 8080
ENDPOINT = f"{THALABUS_PROTOCOL}://{THALABUS_HOSTNAME}:{THALABUS_PORT}/v1"
SESSION_ID_PREFIX = "sdk-"
SESSIONS_MAX = 5
USER_ID = ""                            # replace as appropriate
TOKEN = "your thalabus API token"       # replace as appropriate
KEEP_ALIVE = False                      # True to keep the RemoteSessions running after this program has ended

async def task(rs: RemoteSession, task_arg: dict):
    # processes a single file
    # input: task_arg = {"file": str}

    try:
        log(INFO, f"Executing task with arg: {task_arg}")
        
        # read the file that contains the attachment
        filename = task_arg["file"]
        with open(filename, "r") as f:
            file_text = f.read()
            log(DEBUG, f"Read file: {filename}")

        # submit the attachment to the remote session
        log(DEBUG, f"Submitting attachment to remote session: {rs.id}")
        await rs.submit_attachment(file_text)

        # submit a message to the remote session, requesting a JSON output
        log(DEBUG, f"Submitting message to remote session: {rs.id}")
        await rs.submit_message(
            "Output a Json structure as indicated, in English language, where you use the attachment as source of information.", 
            json_output=JSON_OUTPUT,
            recommended_plan="plan_simple_answer"       # optional: this speeds processing up
        )

        # get, print and save the response to a .json file (use the same filename as the input file, replace .txt with .json)
        response = await rs.get_response()
        if response is not None:
            log(INFO, f"Response: {response}")

            # remove the unnecessary attributes, add the filename
            filename = filename.replace(".txt", "")
            filename_json = os.path.basename(filename)
            response["filename"] = filename_json + ".pdf"
            if "guid" in response:
                del response["guid"]

            with open(f"{filename}.json", "w") as f:
                if isinstance(response, ContainerMessage):
                    # extract the message from the container
                    response_pretty_printed = response.msg_message
                elif isinstance(response, dict) or isinstance(response, list):
                    # Pretty-print the response
                    response_pretty_printed = json.dumps(response, indent=4)
                else:
                    # response is a string: copy as-is
                    response_pretty_printed = response
                    
                f.write(response_pretty_printed)
                log(DEBUG, f"Saved response to file: {filename}.json")
        else:
            log(ERROR, f"Response is None")

    except Exception as e:
        log(ERROR, f"Exception: {e}")

def find_files(folder: str, pattern: str) -> List[str]:
    # lists the files in the folder, matching a regex pattern
    files = []
    try:
        for root, dirs, filenames in os.walk(folder):
            for filename in fnmatch.filter(filenames, pattern):
                files.append(os.path.join(root, filename))
    except Exception as e:
        log(ERROR, f"Error finding files: {e}")
    return files

async def main_async(keep_alive:bool=False):
    log_init()
    log(INFO, f"STARTUP {__name__}")

    try:
        # determine input data for the processes
        files = find_files(FOLDER, PATTERN)
        task_args = [{"file": file} for file in files]
        print(f"There are {len(task_args)} files matching your pattern.")
        user_input = input("Do you want to proceed? (Press ENTER to continue or 'n' to exit): ")
        if user_input.lower() == 'n':
            print("Exiting without creating a new session.")
            sys.exit(0)

        # launch the processes in a pool of remote connections to thalabus server
        remote_pool = RemoteSessionPool(SESSIONS_MAX, ENDPOINT, TOKEN, SESSION_ID_PREFIX, USER_ID)
        await remote_pool.pool_execute(task, task_args, keep_alive=keep_alive)
    except Exception as e:
        log(FATAL, f"Exception: {e}")

    log(INFO, f"SHUTDOWN {__name__}")
    log_exit()


if __name__ == "__main__":
    asyncio.run(main_async(keep_alive=KEEP_ALIVE))
```


# License
This project is licensed under the MIT License.
