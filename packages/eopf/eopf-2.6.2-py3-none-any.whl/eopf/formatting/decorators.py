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
decorators.py

formatting decorators

"""
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from eopf.exceptions import FormattingDecoratorMissingUri
from eopf.formatting import EOFormatterFactory

CALLABLE_TYPE = TypeVar("CALLABLE_TYPE", bound="Callable[..., Any]")


class formatable_method:
    """Decorator class to allow class methods to allow formatting of the return\

    Parameters
    ----------
    fn: Callable[[Any], Any]
        a method of class which has a return

    Attributes
    ----------
    fn: Callable[[Any], Any]
        a method of class which has a return
    parent_obj: Any
        the object corresponding to the decorated method

    Examples
    --------
    >>> class example(object):
    ...     def __init__(self, val:int):
    ...         self.d: Dict[str, int] = {"a_val": val}
    ...
    ...     @formatable_method
    ...     def get_val(self, url: str):
    ...         return self.d[url]
    >>> ex = example(2)
    >>> ex.get_val("to_str(a_val)")
    """

    def __init__(self, decorator_factory: Optional[EOFormatterFactory] = None, formatable: bool = True) -> None:
        self.formatable = formatable
        if decorator_factory:
            self.decorator_factory = decorator_factory
        else:
            self.decorator_factory = EOFormatterFactory()

    def __call__(self, fn: CALLABLE_TYPE) -> CALLABLE_TYPE:
        def inner(this: Any, formatable: str, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
            # parse the path, which should always be the first argument
            _, formatter, formatter_stripped_uri = self.decorator_factory.get_formatter(formatable)
            # replace the first argument with the formatter_stripped_uri

            # call the decorated function
            decorated_method_ret = fn(this, formatter_stripped_uri, *args, **kwargs)
            if self.formatable and formatter is not None:
                return formatter.format(decorated_method_ret)

            return decorated_method_ret

        return inner  # type: ignore


class reverse_formatable_method:
    """Decorator class to allow class methods to reverse the formatting of the return\

    Parameters
    ----------
    fn: Callable[[Any], Any]
        a method of class which has a return

    Attributes
    ----------
    fn: Callable[[Any], Any]
        a method of class which has a return
    parent_obj: Any
        the object corresponding to the decorated method

    Examples
    --------
    >>> class example(object):
    ...     def __init__(self, val:int):
    ...         self.d: Dict[str, int] = {"a_val": val}
    ...
    ...     @reverse_formatable_method
    ...     def set_val(self, url: str):
    ...         return self.d[url]
    >>> ex = example(2)
    >>> ex.set_val("to_str(a_val)")
    """

    def __init__(self, decorator_factory: Optional[EOFormatterFactory] = None, formatable: bool = True) -> None:
        self.formatable = formatable
        if decorator_factory:
            self.decorator_factory = decorator_factory
        else:
            self.decorator_factory = EOFormatterFactory()

    def __call__(self, fn: CALLABLE_TYPE) -> CALLABLE_TYPE:
        def inner(this: Any, formatable: str, arg_to_reverse: Any, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
            # parse the path, which should always be the first argument
            _, formatter, formatter_stripped_uri = self.decorator_factory.get_formatter(formatable)
            # replace the first argument with the formatter_stripped_uri
            if self.formatable and formatter is not None:
                arg_to_reverse = formatter.reverse_format(arg_to_reverse)
            # call the decorated function
            decorated_method_ret = fn(this, formatter_stripped_uri, arg_to_reverse, *args, **kwargs)

            return decorated_method_ret

        return inner  # type: ignore


class unformatable_method(formatable_method):
    """Decorator class to allow class methods to ignore formatting of the return\

    Parameters
    ----------
    fn: Callable[[Any], Any]
        a method of class which has a return

    Attributes
    ----------
    fn: Callable[[Any], Any]
        a method of class which has a return
    parent_obj: Any
        the object corresponding to the decorated method

    Examples
    --------
    >>> class example(object):
    ...     def __init__(self, val:int):
    ...         self.d: Dict[str, int] = {"a_val": val}
    ...
    ...     @unformatable_method
    ...     def get_val(self, url: str):
    ...         return self.d[url]
    >>> ex = example(2)
    >>> ex.get_val("to_str(a_val)")
    """

    def __init__(
        self,
        decorator_factory: Optional[EOFormatterFactory] = None,
        formatable: bool = False,
    ) -> None:
        super().__init__(decorator_factory, formatable)


def formatable_func(fn: Callable[[Any], Any]) -> Any:
    """Decorator function used to allow formatting of the return

    Parameters
    ----------
    fn: Callable[[Any], Any]
        callable function

    Returns
    -------
    Any: formatted return of the wrapped function

    Examples
    --------
    >>> @formatable
    >>> def get_data(key, a_float):
    ...     unformatted_data = read_data(key)
    ...     return unformatted_data * a_float
    >>> ret = get_data('to_float(/tmp/data.nc)', a_float=3.14)
    """

    @wraps(fn)
    def wrap(*args: Any, **kwargs: Any) -> Any:
        """Any function that received a path, url or key can be formatted"""

        if len(args) < 1:
            raise FormattingDecoratorMissingUri("The decorated function does not contain a URI")

        # parse the path, which should always be the first argument
        _, formatter, formatter_stripped_uri = EOFormatterFactory().get_formatter(args[0])

        # replace the first argument with the formatter_stripped_uri
        lst_args = list(args)
        lst_args[0] = formatter_stripped_uri
        new_args = tuple(lst_args)

        # call the decorated function
        decorated_func_ret = fn(*new_args, **kwargs)
        if formatter is not None:
            return formatter.format(decorated_func_ret)
        return decorated_func_ret

    return wrap
