"""Useful utilities."""

from typing import Any

_truthy = ('1', 'on', 'y', 'yes', 'true')

_falsy = ('', '0', 'off', 'n', 'no', 'false')


def is_truthy(arg: Any) -> bool:
    """
    Check if the given argument is truthy.

    Parameters
    ----------
    arg : Any
        The argument to check.

    Returns
    -------
    bool
        True if ``arg`` is truthy.

    Examples
    --------
    >>> is_truthy('ON')
    True
    >>> is_truthy(10)
    False
    """
    return str(arg).lower() in _truthy


def is_falsy(arg: Any) -> bool:
    """
    Check if the given argument is falsy.

    Parameters
    ----------
    arg : Any
        The argument to check.

    Returns
    -------
    bool
        True if ``arg`` is falsy.

    Examples
    --------
    >>> is_falsy('NO')
    True
    >>> is_falsy(-1)
    False
    """
    return str(arg).lower() in _falsy


__all__ = ['is_truthy', 'is_falsy']
