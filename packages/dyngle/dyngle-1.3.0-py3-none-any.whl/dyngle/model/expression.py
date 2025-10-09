from typing import Callable

from dyngle.error import DyngleError
from dyngle.model.live_data import LiveData
from dyngle.model.safe_path import SafePath

from datetime import datetime as datetime, date, timedelta
import math
import json
import re
import yaml

from dyngle.model.template import Template


def formatted_datetime(dt: datetime, format_string=None) -> str:
    """Safe datetime formatting using string operations"""
    if format_string is None:
        format_string = "{year:04d}{month:02d}{day:02d}"
    components = {
        'year': dt.year,
        'month': dt.month,
        'day': dt.day,
        'hour': dt.hour,
        'minute': dt.minute,
        'second': dt.second,
        'microsecond': dt.microsecond,
        'weekday': dt.weekday(),  # Monday is 0
    }
    return format_string.format(**components)


GLOBALS = {
    "__builtins__": {
        # Basic data types and conversions
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,

        # Essential functions
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
        "type": type
    },

    # Mathematical operations
    "math": math,

    # Date and time handling
    "datetime": datetime,
    "date": date,
    "timedelta": timedelta,
    "formatted": formatted_datetime,

    # Data parsing and manipulation
    "json": json,
    "yaml": yaml,
    "re": re,

    # Safe Path-like operations (within cwd)
    "Path": SafePath
}


def _evaluate(expression: str, locals: dict) -> str:
    """Evaluate a Python expression with safe globals and user data context.

    Safely evaluates a Python expression string using a restricted set of
    global functions and modules, combined with user-provided data. The
    expression is evaluated in a sandboxed environment that includes basic
    Python built-ins, mathematical operations, date/time handling, and data
    manipulation utilities.

    Parameters
    ----------
    expression : str
        A valid Python expression string to be evaluated.
    data : dict
        Dictionary containing variables and values to be made available during
        expression evaluation. Note that hyphens in keys will be replaced by
        underscores to create valid Python names.

    Returns
    -------
    str
        String representation of the evaluated expression result. If the result
        is a tuple, returns the string representation of the last element.

    Raises
    ------
    DyngleError
        If the expression contains invalid variable names that are not found in
        the provided data dictionary or global context.
    """
    try:
        result = eval(expression, GLOBALS, locals)
    except KeyError as error:
        raise DyngleError(f"The following expression contains " +
                          f"invalid name '{error}:\n{expression}")

    # Allow the use of a comma to separate sub-expressions, which can then use
    # warus to set values, and only the last exxpression in the list returns a
    # value.
    result = result[-1] if isinstance(result, tuple) else result

    return result


# The 'expression' function returns the expression object itself, which is
# really just a function.

def expression(text: str) -> Callable[[dict], str]:
    """Generate an expression, which is a function based on a string
    expression"""

    def definition(live_data: LiveData | dict | None = None) -> str:
        """The expression function itself"""

        # Allow for blankness and testability
        live_data = LiveData(live_data)

        # Translate names to underscore-separated instead of hyphen-separated
        # so they work within the Python namespace.

        items = live_data.items() if live_data else ()
        locals = LiveData({k.replace('-', '_'): v for k, v in items})

        # Create a resolve function which allows references using the hyphen
        # syntax too

        def resolve(key):
            return live_data.resolve(key, str_only=False)
        locals = locals | {'resolve': resolve}

        # Perform the Python eval, expanded above
        return _evaluate(text, locals)

    return definition
