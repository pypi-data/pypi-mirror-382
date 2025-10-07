from __future__ import annotations

from numbers import Number
from typing import Literal, Iterable, Any

import inflect

from .exceptions import CircuitError
from .policies import ReturnValuePolicy

p = inflect.engine()

_WordLike = str | inflect.Word


def normalize_exception_types(
    types_iter: Iterable[type[BaseException]] | None,
) -> tuple[type[BaseException], ...]:
    if not types_iter:
        return tuple()
    return tuple(types_iter)


def should_record_for_exception(
    exc: BaseException,
    ignore_ex: tuple[type[BaseException], ...],
    on_ex: tuple[type[BaseException], ...],
) -> bool:
    """
    Decide whether an exception should be considered a failure, given
    ignore_ex and on_ex tuples.
    - If `ignore_ex` contains exc type (isinstance), do NOT record.
    - If `on_ex` is non-empty, record only if exc is instance of an entry in `on_ex`.
    - If `on_ex` is empty, record by default (unless ignored).
    """
    if ignore_ex and isinstance(exc, ignore_ex):
        return False
    if on_ex:
        return isinstance(exc, on_ex)
    return True


def should_record_for_returnval(
    policy: ReturnValuePolicy | None, result: Any
) -> tuple[bool, str] | None:
    """
    Decide whether a returned result should be treated as a failure according to
    the given ReturnValuePolicy.

    Returns:
      - tuple(True, reason) if the policy marks the result as a failure
      - None if the result is considered OK (no failure)
    """
    if policy is None:
        return None

    if not isinstance(policy, ReturnValuePolicy):
        raise CircuitError("Invalid return value policy") from ValueError(  # noqa
            f"policy must be a ReturnValuePolicy instance, got {policy!r}"
        )

    def _extract_by_accessor(
        obj: Any, accessor: str, args: tuple | None, kwargs: dict | None
    ) -> tuple[bool, Any]:
        """
        Try to obtain value via accessor.
        Returns:
             tuple(True, value) on success,  tuple(False, None) on failure.
        This is tolerant and will not raise.
        """
        if not accessor:
            return False, None
        try:
            parts = accessor.split(".")
            cur = obj
            for part in parts[:-1]:
                # prefer attribute first, then mapping
                if hasattr(cur, part):
                    cur = getattr(cur, part)
                elif isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                else:
                    return False, None

            last = parts[-1]
            # final resolution
            if hasattr(cur, last):
                attr = getattr(cur, last)
                if callable(attr):
                    try:
                        return True, attr(*(args or ()), **(kwargs or {}))
                    except Exception:
                        return False, None
                else:
                    return True, attr
            elif isinstance(cur, dict) and last in cur:
                return True, cur[last]
            else:
                return False, None
        except Exception:
            # Any unexpected error, treat as accessor failure (no match)
            return False, None

    subject = result
    if policy.retval_accessor is not None:
        ok, val = _extract_by_accessor(
            result,
            str(policy.retval_accessor),
            policy.retval_accessor_args,
            policy.retval_accessor_kwargs,
        )
        if ok:
            subject = val
        # else: leave subject as original result

    if policy.retval_none is not None:
        if subject is None:
            return True, "return value is None (policy.retval_none)"

    if policy.retval is not None:
        try:
            if subject == policy.retval:
                return True, f"return value equals policy.retval ({policy.retval!r})"
        except Exception:
            # comparison failed, ignore
            pass

    if policy.retval_in is not None:
        try:
            if subject in policy.retval_in:
                return True, f"return value in policy.retval_in ({policy.retval_in!r})"
        except TypeError:
            # iterable may not be hashable; fallback to tolerant linear scan
            try:
                for item in policy.retval_in:
                    try:
                        if subject == item:
                            return (
                                True,
                                f"return value equals an item in policy.retval_in ({item!r})",
                            )
                    except Exception:
                        continue
            except Exception:
                # retval_in not iterable or other issue, ignore
                pass

    # no rule matched
    return None


def effective_policy_overrides(
    cb,
    service: str,
    override_scheme: Literal["merge", "prioritize_method_args"] = "merge",
    *,
    ignore_exceptions: Iterable[type[BaseException]] | None = None,
    on_exceptions: Iterable[type[BaseException]] | None = None,
    on_retval_policy: ReturnValuePolicy | None = None,
) -> tuple[
    tuple[type[BaseException], ...],
    tuple[type[BaseException], ...],
    ReturnValuePolicy | Any,
]:
    """
    Compute effective tuples/values for a call:
    - merge: merge method-level args with service policy.
    - prioritize_method_args: use method-level args if provided, otherwise use service policy.
    - returns (ignore_ex_tuple, on_ex_tuple, effective_retval_policy)
    """

    from ._breaker import CircuitBreaker

    if not isinstance(cb, CircuitBreaker):
        raise CircuitError("cb must be a CircuitBreaker instance in")

    policy = cb.policy_for(service)

    if override_scheme == "merge":
        ignore_tuple = tuple(
            set(normalize_exception_types(policy.ignore_exceptions))
            | set(normalize_exception_types(ignore_exceptions))
        )
        onex_tuple = tuple(
            set(normalize_exception_types(policy.on_exceptions))
            | set(normalize_exception_types(on_exceptions))
        )
    else:
        ignore_tuple = (
            normalize_exception_types(ignore_exceptions)
            if ignore_exceptions is not None
            else normalize_exception_types(policy.ignore_exceptions)
        )
        onex_tuple = (
            normalize_exception_types(on_exceptions)
            if on_exceptions is not None
            else normalize_exception_types(policy.on_exceptions)
        )

    retval_pol = (
        on_retval_policy if on_retval_policy is not None else policy.on_retval_policy
    )
    return ignore_tuple, onex_tuple, retval_pol


def ordinal(num: Number):
    return p.ordinal(num)


def singularize(item: _WordLike):
    text = p.singular_noun(item)
    if not text:
        return item
    return text


def pluralize(item: _WordLike):
    return p.plural(item)


def num_to_words(num: Number):
    return p.number_to_words(num)


def inflect_str(item: _WordLike, count: Any, include_count: bool = False) -> str:
    if item is None:
        raise ValueError("item must be a non-empty string")

    if not str(item).strip():
        return ""

    try:
        cnt = int(count)
    except (TypeError, ValueError):
        cnt = 0

    word = item

    verbs_map = {
        "have": ("has", "have"),
        "has": ("has", "have"),
        "is": ("is", "are"),
        "are": ("is", "are"),
        "was": ("was", "were"),
        "were": ("was", "were"),
        "does": ("does", "do"),
        "do": ("does", "do"),
    }

    lw = word.lower()
    if lw in verbs_map:
        singular, plural = verbs_map[lw]
        chosen = singular if cnt == 1 else plural
        return f"{cnt} {chosen}" if include_count else chosen

    try:
        plural_form = p.plural(word)
        singular_guess = p.singular_noun(word) or word
    except Exception:
        if word.endswith("y") and len(word) > 1 and word[-2].lower() not in "aeiou":
            plural_form = word[:-1] + "ies"
        elif word.endswith(("s", "x", "z", "ch", "sh")):
            plural_form = word + "es"
        else:
            plural_form = word + "s"
        singular_guess = word[:-1] if word.endswith("s") and len(word) > 1 else word

    def preserve_case(src: str, target: str) -> str:
        if src.istitle():
            return target.capitalize()
        if src.isupper():
            return target.upper()
        return target

    singular = preserve_case(word, str(singular_guess))
    plural = preserve_case(word, plural_form)

    if cnt == 1:
        return f"{cnt} {singular}" if include_count else singular

    return f"{cnt} {plural}" if include_count else plural
