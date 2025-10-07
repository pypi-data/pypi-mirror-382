from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, TypeVar, Union, Optional, cast

from typeguard import TypeCheckError, typechecked as _typechecked

from .exceptions import CircuitError

F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def _wrap_decorated(func: F, decorated: Callable[..., Any]) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return decorated(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, CircuitError):
                raise

            if TypeCheckError is not None and isinstance(exc, TypeCheckError):
                raise CircuitError(
                    f"type validation failed for {func.__name__}: {str(exc)}"
                ) from exc
            raise

    return cast(F, wrapper)


def _wrap_class_callables(original_cls: type, decorated_cls: type) -> type:
    """
    For each callable attribute on the original class, replace the decorated class's
    attribute with a wrapper that converts TypeCheckError -> CircuitError.
    Handle normal methods, staticmethod, classmethod and property accessors.
    """
    for name, orig_attr in vars(original_cls).items():
        if name.startswith("__") and name.endswith("__"):
            continue

        if not hasattr(decorated_cls, name):
            continue

        decorated_attr = getattr(decorated_cls, name)

        if isinstance(orig_attr, staticmethod):
            orig_fn = orig_attr.__func__
            dec_fn = (
                decorated_attr.__func__
                if isinstance(decorated_attr, (staticmethod, classmethod))
                else decorated_attr
            )
            wrapped = _wrap_decorated(orig_fn, dec_fn)
            setattr(decorated_cls, name, staticmethod(wrapped))
            continue

        if isinstance(orig_attr, classmethod):
            orig_fn = orig_attr.__func__
            dec_fn = (
                decorated_attr.__func__
                if isinstance(decorated_attr, (staticmethod, classmethod))
                else decorated_attr
            )
            wrapped = _wrap_decorated(orig_fn, dec_fn)
            setattr(decorated_cls, name, classmethod(wrapped))
            continue

        if isinstance(orig_attr, property):
            dec_prop = getattr(decorated_cls, name)
            fget = None
            fset = None
            fdel = None
            if orig_attr.fget and dec_prop.fget:
                fget = _wrap_decorated(orig_attr.fget, dec_prop.fget)
            if orig_attr.fset and dec_prop.fset:
                fset = _wrap_decorated(orig_attr.fset, dec_prop.fset)
            if orig_attr.fdel and dec_prop.fdel:
                fdel = _wrap_decorated(orig_attr.fdel, dec_prop.fdel)
            setattr(decorated_cls, name, property(fget, fset, fdel))
            continue

        if callable(orig_attr):
            dec_fn = decorated_attr
            try:
                wrapped = _wrap_decorated(orig_attr, dec_fn)
                setattr(decorated_cls, name, wrapped)
            except Exception:
                # be conservative: if wrapping fails for some reason, leave decorated attr as-is
                logger.debug(
                    "could not wrap %s.%s; leaving decorated attribute",
                    original_cls.__name__,
                    name,
                )
            continue

    return decorated_cls


def typechecked(func: Optional[F] = None) -> Union[Callable[[F], F], F]:
    if _typechecked is None:

        def decorator(f: F) -> F:
            return f

        if func is None:
            return decorator  # used as @typechecked()
        return decorator(func)

    if func is not None:
        # Used as @typechecked (without parentheses)
        try:
            decorated = _typechecked(func)
            if isinstance(decorated, type):
                return cast(F, _wrap_class_callables(type(func), decorated))
            return _wrap_decorated(func, decorated)
        except Exception as exc:
            raise CircuitError(
                f"failed to enable runtime type checks for {func.__name__}: {str(exc)}"
            ) from exc
    else:
        # Used as @typechecked()
        def inner_decorator(f: F) -> F:
            try:
                d = _typechecked(f)  # noqa
                if isinstance(d, type):
                    return cast(F, _wrap_class_callables(type(f), d))
                return _wrap_decorated(f, d)
            except Exception as ex:
                raise CircuitError(
                    f"failed to enable runtime type checks for {f.__name__}: {str(ex)}"
                ) from ex

        return inner_decorator
