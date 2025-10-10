import os

SUBPROCESS_ENV_NAME = 'DCNR_SPRING_SUBPROCESS'

def is_subprocess() -> bool:
    return os.getenv(SUBPROCESS_ENV_NAME, '0').lower() in ('1', 'true', 'yes')


__all__ = [
    "SubprocessArguments",
    "SubprocessPickleRunner",
    "SubprocessPickle",
    "SubprocessResult",
    "SUBPROCESS_ENV_NAME",
    "is_subprocess"
]

from .subprocess_arguments import SubprocessArguments
from .subprocess_pickle_runner import SubprocessPickleRunner
from .subprocess_pickle import SubprocessPickle
from .subprocess_result import SubprocessResult
