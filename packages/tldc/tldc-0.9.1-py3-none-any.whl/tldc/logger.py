import sys
from functools import wraps

def _logger(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return result
        except BaseException as e:
            print(f"[error] {repr(e)}")
            sys.exit(-1)
    return wrapper

def logger(msg, level="info"):
    print(f"[{level}] {msg}")