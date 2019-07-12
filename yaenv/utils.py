"""Useful utilities."""

from typing import Any, Dict, Iterator

try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse  # noqa: T484

_truthy = ('1', 'on', 'y', 'yes', 'true')

_falsy = ('', '0', 'off', 'n', 'no', 'false')


def iteritems(items):  # noqa: D103
    # type: (Dict) -> Iterator
    return getattr(items, 'iteritems', items.items)()


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
    return str(arg).lower() in _truthy


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
    return str(arg).lower() in _falsy


__all__ = ['is_truthy', 'is_falsy', 'urlparse', 'iteritems']
