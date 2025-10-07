#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
functions_utils.py

Utility functions iteration, dict search etc

"""

import ast
import json
import multiprocessing
import os.path
import re
import traceback
import zlib
from enum import Flag
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    Optional,
    Sized,
    Type,
    TypeVar,
)

import cloudpickle

from eopf.exceptions.errors import ExceptionWithExitCode, TimeOutError

if TYPE_CHECKING:
    from multiprocessing.queues import Queue

T = TypeVar("T")


def nested_apply(nested_dict: Any, func: Callable[[Any], Any]) -> Any:
    """Apply a function to each element of nested_dict and return resulting dictionary."""
    if isinstance(nested_dict, Mapping):
        return {k: nested_apply(v, func) for k, v in nested_dict.items()}
    if isinstance(nested_dict, list):
        out_list = []
        for t in nested_dict:
            out_list.append(nested_apply(t, func))
        return out_list
    return func(nested_dict)


def not_none(obj: Optional[T]) -> T:
    """Check that obj is not None. Raises TypeError if it is.

    This is meant to help get code to type check that uses Optional types.

    """
    if obj is None:
        raise TypeError("object is unexpectedly None")
    return obj


def expand_env_var_in_dict(indict: dict[Any, Any]) -> dict[Any, Any]:
    """
    Recursively go throuth the dict to expand the env vars in it
    Parameters
    ----------
    indict

    Returns
    -------
    resolvec env var dict

    """
    out_dict = {}
    for key in indict.keys():
        if isinstance(indict[key], dict):
            out_dict[key] = expand_env_var_in_dict(indict[key])
        else:
            if isinstance(indict[key], (str, bytes, os.PathLike)):
                out_dict[key] = os.path.expandvars(indict[key])
            else:
                out_dict[key] = indict[key]
    return out_dict


def is_last(iterable: Iterable[Any]) -> Iterator[tuple[Any, bool]]:
    """
    Utility function to iterate on collections and having the info if it is the last one or not
    in case you need to do something different on the last element

    Parameters
    ----------
    iterable : an iterable to iterate on

    Returns
    -------
    generate tuple of (item, is_last) on the iterable
    """
    iter_ = iter(iterable)
    try:
        nextitem = next(iter_)
    except StopIteration:
        pass
    else:
        item = nextitem
        while True:
            try:
                nextitem = next(iter_)
                yield item, False
            except StopIteration:
                yield nextitem, True
                break
            item = nextitem


def resolve_path_in_dict(data: dict[str, Any], path: str, separator: str = "/") -> Any:
    """Access a nested dictionary element using a POSIX-style path.
    Ex "/truc/machin/subff"

    Will throw key error if not found
    """
    result = resolve_paths_in_dict_with_regex(data, path, separator)
    if len(result) > 1:
        raise KeyError(f"More than one value found for {path} in dict")
    if len(result) == 0:
        raise KeyError(f"No value found for {path} in dict")
    return next(iter(result.items()))[1]


def resolve_paths_in_dict_with_regex(data: dict[str, Any], path: str, separator: str = "/") -> dict[str, Any]:
    """Access a nested dictionary element using a POSIX-style path with regex possible patterns.
    Ex "/.*/.*/subff"

    Will throw key error if not found
    """
    if not isinstance(data, dict):
        raise TypeError("Only dict allowed, check path/data")
    result = {}
    # ensure starts with the separator
    path = path if path.startswith(separator) else f"{separator}{path}"
    keys = path.strip(separator).split(separator)

    key = keys[0]
    for t in data.keys():
        if re.fullmatch(key, t):
            # Not the last part
            if len(keys) > 1:
                if isinstance(data[t], dict):  # only look in sub dict as the path is not finished
                    sub_result = resolve_paths_in_dict_with_regex(
                        data[t],
                        separator.join(keys[1:]),
                        separator=separator,
                    )
                    for k, v in sub_result.items():
                        result[t + separator + k] = v
            else:
                result[t] = data[t]
    return result


def get_all_paths_in_dict(indict: dict[str, Any]) -> list[str]:
    """
    Get all possible posix path in dict

    """
    result = []
    for p, val in indict.items():
        if isinstance(val, dict):
            result.extend([os.path.join(p, r) for r in get_all_paths_in_dict(val)])
        else:
            result.append(p)
    return result


def nested_dict_from_paths(paths: list[str]) -> dict[str, Any]:
    """
    Create a dictr hierarchy based on a list of posix path
    leaf value will be set to "TOBEDEFINED"

    Parameters
    ----------
    paths : list of posix like path to create

    Returns
    -------
    A initialized tree structure

    """
    root: dict[str, Any] = {}
    for path in paths:
        parts = path.split("/")
        current = root
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = "TOBEDEFINED"
    return root


def flatten_values(data: Any) -> Generator[str, None, None]:
    """Recursively extract all values from a nested dictionary or list."""
    if isinstance(data, dict):
        for value in data.values():
            yield from flatten_values(value)
    elif isinstance(data, list):
        for item in data:
            yield from flatten_values(item)
    else:
        yield str(data)


def compute_crc(data: Any, digits: int = 8) -> str:
    """Compute a fixed-length Hexadecimal CRC string from all values in a nested dictionary."""
    all_values = "".join(flatten_values(data))
    crc_value = zlib.crc32(all_values.encode("utf-8"))
    return f"{crc_value & ((1 << (4 * digits)) - 1):0{digits}X}"


class SafeAstEvaluator(ast.NodeVisitor):
    """
    Safe evaluator for security reason we can't let an eval() to be freely done
    """

    SAFE_NODES = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Str,
        ast.Name,
        ast.Load,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.Set,
        ast.Subscript,
        ast.Index,
        ast.Slice,
        ast.Compare,
        ast.BoolOp,
        ast.operator,
        ast.unaryop,
        ast.And,
        ast.Or,
        ast.IfExp,
        ast.Constant,
        ast.Call,
        ast.Attribute,
        ast.Mult,
        ast.Add,
        ast.Lt,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitAnd,
        ast.BitXor,
        ast.FloorDiv,
        ast.UAdd,
        ast.USub,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,
        ast.NotIn,
    }
    SAFE_OPERATORS = {
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitAnd,
        ast.BitXor,
        ast.FloorDiv,
        ast.UAdd,
        ast.USub,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,
        ast.NotIn,
    }

    def generic_visit(self, node: Any) -> Any:
        if type(node) not in self.SAFE_NODES:
            raise ValueError(f"Unsafe operation: {type(node).__name__}")
        super().generic_visit(node)

    def visit_Import(self, node: Any) -> Any:
        # Capture all import statements
        raise ValueError(f"Unsafe operation: {type(node).__name__}")

    def visit_ImportFrom(self, node: Any) -> Any:
        # Capture imports like 'from os import path'
        raise ValueError(f"Unsafe operation: {type(node).__name__}")

    def visit_BinOp(self, node: Any) -> Any:
        if type(node.op) not in self.SAFE_OPERATORS:
            raise ValueError(f"Unsafe operator: {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_Attribute(self, node: Any) -> Any:
        # Allow attribute access but block double underscores (e.g., "__dict__")
        if node.attr.startswith("__"):
            raise ValueError(f"Unsafe attribute access: {node.attr}")
        self.generic_visit(node)

    def visit_Name(self, node: Any) -> Any:
        if node.id.startswith("__"):
            raise ValueError(f"Unsafe element name: {node.id}")
        self.generic_visit(node)

    def visit_Call(self, node: Any) -> Any:
        self.generic_visit(node)


def safe_eval(
    expression: str,
    variables: Optional[dict[str, Any]] = None,
    modules: Optional[dict[str, Any]] = None,
) -> Any:
    """
    Evaluate a Python expression with controlled access to variables and modules.

    Args:
        expression (str): The expression to evaluate.
        variables (dict): A dictionary of variables to make available to the evaluation.
        modules (dict): A dictionary of module names and references to include in the evaluation.

    Returns:
        The result of the evaluated expression.
    """
    # Parse and validate the expression
    parsed_expr = ast.parse(expression, mode="eval")
    SafeAstEvaluator().visit(parsed_expr)

    # Validate variables
    variables = variables or {}
    for var_name, var_value in variables.items():
        if var_name.startswith("__"):
            raise ValueError(f"Unsafe variable name: {var_name}")
        if callable(var_value):
            raise ValueError(f"Unsafe variable type: {var_name} is callable")

    variables = variables or {}
    modules = modules or {}

    # Combine allowed modules into the global scope for `eval`
    allowed_globals = {"__builtins__": None, **modules}

    # Use `variables` as the local scope
    # Safe evak as we control the allowed env
    try:
        return eval(expression, allowed_globals, variables)  # nosec # pylint: disable=eval-used
    except TypeError as e:
        raise TypeError(
            f"Error while evaluating {expression} with var: {variables} " f"and globals : {allowed_globals}",
        ) from e


FlagLike = TypeVar("FlagLike", bound=Flag)


def parse_flag_expr(expr: str, enum_cls: Type[FlagLike]) -> FlagLike:
    """
    Parse a fladLike expression to the corresponding flagLike

    "PAUSED | STUCK_SPILL" -> TestFlags.PAUSED | TestFlags.STUCK_SPILL

    Parameters
    ----------
    expr : expression to parse
    enum_cls : Type of enum flaglike wanted

    Returns
    -------
    The evaluated flaglike value

    """
    # Create a controlled globals dict for eval
    allowed = dict(enum_cls.__members__.items())
    try:
        # nosec : we remove all the builtins and only allow the one we want thus can't do injections
        return eval(expr, {"__builtins__": None}, allowed)  # nosec # pylint: disable=eval-used
    except Exception as e:
        raise ValueError(f"Invalid flag expression: {expr}") from e


# Retrieved from https://github.com/nerandell/camelsnake/blob/main/camelsnake.py
CAMEL_TO_SNAKE_PATTERN = re.compile("(.)([A-Z][a-z]+)")
CAMEL_TO_SNAKE_DIGIT_PATTERN = re.compile("([a-z0-9])([A-Z])")
SNAKE_TO_CAMEL_PATTERN = re.compile("_(.)")


def camel_to_snake(input_str: str) -> str:
    """
    Convert a string from camel case to snake case using regular expressions.

    Args:
        input_str (str): A string in camel case.

    Returns:
        str: The same string in snake case.

    Examples:
        >>> camel_to_snake('helloWorld')
        'hello_world'
        >>> camel_to_snake('MyHTTPRequest')
        'my_http_request'
    """
    # Replace any occurrence of a lowercase letter followed by an uppercase letter with
    # the lowercase letter, an underscore, and the uppercase letter
    snake_str = CAMEL_TO_SNAKE_PATTERN.sub(r"\1_\2", input_str)
    # Replace any occurrence of a lowercase letter or digit followed by an uppercase letter with
    # the lowercase letter or digit, an underscore, and the uppercase letter
    return CAMEL_TO_SNAKE_DIGIT_PATTERN.sub(r"\1_\2", snake_str).lower()


def snake_to_camel(input_str: str) -> str:
    """
    Convert a string from snake case to camel case using regular expressions.

    Args:
        input_str (str): A string in snake case.

    Returns:
        str: The same string in camel case.

    Examples:
        >>> snake_to_camel('hello_world')
        'helloWorld'
        >>> snake_to_camel('my_http_request')
        'myHttpRequest'
    """
    # Find any underscore character followed by a lowercase letter,
    # and replace the underscore and lowercase letter with the uppercase letter
    # using a lambda function
    return SNAKE_TO_CAMEL_PATTERN.sub(lambda m: m.group(1).upper(), input_str)


def run_with_timeout(func: Callable[..., Any], timeout: int, *args: Any, **kwargs: Any) -> Any:
    """
    Runs `func(*args, **kwargs)` in a subprocess and enforces timeout.

    Returns:
        The result of the function if it completes in time.

    Raises:
        FunctionTimeoutError: If timeout is exceeded.
        Exception: If the function raises any exception.
    """

    def wrapper(queue_in: "Queue[Any]", *args_in: Any, **kwargs_in: Any) -> None:
        try:
            result = func(*args_in, **kwargs_in)
            queue_in.put(("result", result))
        # Catching all exceptions so they can be sent back through the queue.
        except Exception as e:  # pylint: disable=broad-except
            tb_in = traceback.format_exc()
            queue_in.put(("exception", (e, tb_in)))

    queue: "Queue[Any]" = multiprocessing.Queue()
    proc = multiprocessing.Process(target=wrapper, args=(queue, *args), kwargs=kwargs)
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        raise TimeOutError(f"Function '{func.__name__}' timed out after {timeout} seconds.")

    if queue.empty():
        raise RuntimeError(f"Function '{func.__name__}' did not return anything.")

    kind, payload = queue.get()
    if kind == "result":
        return payload
    if kind == "exception":
        exc, tb = payload
        raise ExceptionWithExitCode(f"Function raised exception:\n{tb}") from exc
    raise ExceptionWithExitCode("Unexpected behaviour")


def catch_and_raise(custom_exception: Type[ExceptionWithExitCode]) -> Callable[[...], Any]:
    """
    Decorator to catch an exception and re-brand it
    Parameters
    ----------
    custom_exception : Type of the exception to raise

    Returns
    -------

    """

    def decorator(func: Callable[[...], Any]) -> Callable[[...], Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise custom_exception(f"An error occurred in {func.__name__}: {e}") from e

        return wrapper

    return decorator


AllowedMultiplicity = Literal["exactly_one", "at_least_one", "more_than_one"]


def verify_multiplicity(in_list: Sized, multiplicity: AllowedMultiplicity | int) -> None:
    if multiplicity == "exactly_one":
        if len(in_list) != 1:
            raise ValueError(
                f"List should have exactly one element, found : {len(in_list)}",
            )
        return
    elif multiplicity == "at_least_one":
        if len(in_list) == 0:
            raise ValueError("List should have at least one element, found 0")
        return
    elif multiplicity == "more_than_one":
        if len(in_list) < 2:
            raise ValueError(
                "List should have more than one element",
            )
        return
    elif isinstance(multiplicity, int):
        number_of_res = int(multiplicity)
        if len(in_list) < number_of_res:
            raise ValueError(
                f"List should at least {number_of_res} while only {len(in_list)}",
            )
    else:
        raise ValueError(
            "Unknown multiplicity value : exactly_one, at_least_one," " more_than_one or a digit requested",
        )


def is_serializable(obj: object, method: str = "pickle") -> bool:
    """
    Check if an object is serializable and preserves equality after deserialization.

    Parameters
    ----------
    obj : any
        The object to test.
    method : str
        Serialization method: "pickle" or "json".

    Returns
    -------
    bool
        True if object is serializable and deserialized object is equal.
    """
    if method == "pickle":
        data = cloudpickle.dumps(obj)
        obj2 = cloudpickle.loads(data)
    elif method == "json":
        # JSON: serialize via __dict__ or a custom method if available
        if hasattr(obj, "to_json") and callable(obj.to_json):
            json_str = obj.to_json()
            if hasattr(obj.__class__, "from_json") and callable(obj.__class__.from_json):
                obj2 = obj.__class__.from_json(json_str)
            else:
                return False
        else:
            # fallback: serialize __dict__ for normal objects
            json_str = json.dumps(obj.__dict__)
            obj2 = obj.__class__(**json.loads(json_str))
    else:
        raise ValueError(f"Unknown method: {method}")

    # Compare objects
    return obj == obj2
