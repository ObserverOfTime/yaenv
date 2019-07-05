"""Useful utilities."""

from typing import Any

try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse  # noqa: T484


def is_truthy(arg):
    # type: (Any) -> bool
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
    return str(arg).lower() in ('1', 'on', 'y', 'yes', 'true')


def is_falsy(arg):
    # type: (Any) -> bool
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
    return str(arg).lower() in ('', '0', 'off', 'n', 'no', 'false')


__all__ = ['is_truthy', 'is_falsy', 'urlparse']
