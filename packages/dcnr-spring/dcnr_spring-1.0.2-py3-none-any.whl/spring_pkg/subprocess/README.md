# How To: Implementing External Process Execution with SubprocessPickleRunner

This document describes the process of converting a function to run in an external process using the `SubprocessPickleRunner` class for safe inter-process communication with pickle+base64 encoding.

## Overview

The `SubprocessPickleRunner` provides a robust way to execute Python functions in separate processes, offering benefits like:
- Process isolation (crashes don't affect main process)
- Memory isolation (prevents memory leaks)
- Better error handling and recovery
- Safe binary data transmission using pickle+base64

## Step-by-Step Implementation Process

### Example of main process `main_t.py`

```python
import os
from dcnr_spring.subprocess import SubprocessPickleRunner

# import path to script
from main_s import __file__ as DETECT_PROCESS_FILE

print('path to subprocess script:', DETECT_PROCESS_FILE)

r = SubprocessPickleRunner(script_path=DETECT_PROCESS_FILE)
result = r.execute("Hello world!")

print(result)

```

### Example of subprocess `main_s.py`

```python

from dcnr_spring.subprocess import SubprocessPickle
import os

def testing_print(text:str):
    print("This is a test print statement.", text)
    return f"OK {os.environ['dcnr_spring_SUBPROCESS']}"

def main():
    SubprocessPickle(testing_print).run()

if __name__ == "__main__":
    main()

```