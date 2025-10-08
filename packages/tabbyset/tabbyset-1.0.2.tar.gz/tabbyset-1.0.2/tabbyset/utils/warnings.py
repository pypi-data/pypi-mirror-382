from typing import Type, Optional, TextIO
from warnings import warn_explicit
from functools import wraps
import sys


def _get_caller_filename_and_lineno():
    import inspect
    frame = inspect.currentframe()
    while frame:
        if frame.f_globals.get('__name__') != __name__:
            return frame.f_code.co_filename, frame.f_lineno
        frame = frame.f_back
    return "<unknown>", 0


def libwarn(message, category: Type[Warning] = RuntimeWarning):
    filename, lineno = _get_caller_filename_and_lineno()
    warn_explicit(message=message, category=category, filename=filename, lineno=lineno)


def warn_with_traceback(message: str,
                        category: Type[Warning],
                        filename: str,
                        lineno: int,
                        file: Optional[TextIO] = None):
    import traceback
    log = file if hasattr(file, 'write') else sys.stderr
    log.write(f"{filename}:{lineno}: {category.__name__}: {message}\n")
    traceback.print_stack(file=log)
    log.write("\n")


def get_warn_once_func():
    is_warned = False

    def warn_once(message, category: Type[Warning] = RuntimeWarning):
        nonlocal is_warned
        if not is_warned:
            is_warned = True
            libwarn(message, category)

    return warn_once


def get_warn_once_per_line_func():
    warned_lines = set()

    def warn_once(message, category: Type[Warning] = RuntimeWarning):
        filename, lineno = _get_caller_filename_and_lineno()
        if (filename, lineno) not in warned_lines:
            warned_lines.add((filename, lineno))
            warn_explicit(message=message, category=category, filename=filename, lineno=lineno)

    return warn_once


def experimental_method(func):
    warn_once = get_warn_once_per_line_func()

    @wraps(func)
    def wrapper(*args, **kwargs):
        class_info = args[0].__class__
        warn_once(f"{class_info.__name__}.{func.__name__} is experimental and may change in the future.",
                  category=FutureWarning)
        return func(*args, **kwargs)

    return wrapper
