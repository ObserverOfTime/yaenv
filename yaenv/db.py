"""Database URL parser."""

from typing import Any, Dict, NewType
from urllib import parse as urlparse

from .utils import is_truthy

DBConfig = NewType('DBConfig', Dict[str, Any])
DBConfig.__qualname__ = 'yaenv.db.DBConfig'

# Supported schemes.
SCHEMES: Dict[str, str] = {
    'mysql': 'django.db.backends.mysql',
    'oracle': 'django.db.backends.oracle',
    'pgsql': 'django.db.backends.postgresql',
    'sqlite': 'django.db.backends.sqlite3',
}

# Scheme aliases.
SCHEMES['postgres'] = SCHEMES['pgsql']
SCHEMES['postgresql'] = SCHEMES['pgsql']
SCHEMES['sqlite3'] = SCHEMES['sqlite']

# Register database schemes in URLs.
urlparse.uses_netloc += list(SCHEMES)


def add_scheme(scheme: str, backend: str) -> None:
    """
    Extend the dictionary of supported schemes.

    Parameters
    ----------
    scheme : int
        The scheme of the database.
    backend : str
        The backend of the database.

    Examples
    --------
    >>> add_scheme('mysql-connector', 'mysql.connector.django')
    """
    SCHEMES[scheme] = backend
    urlparse.uses_netloc.append(scheme)


def parse(url: str) -> DBConfig:
    """
    Parse a database URL.

    Parameters
    ----------
    url : str
        The database URL to be parsed.

    Returns
    -------
    DBConfig
        A dictionary that can be used in
        :dj:`django.settings.DATABASES <databases>`.

    Examples
    --------
    >>> parse('mysql://user:pass@127.0.0.1:3306/django')
    {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {}
    }
    """
    # Special case: https://www.sqlite.org/inmemorydb.html.
    if url == 'sqlite://:memory:':
        return DBConfig({
            'ENGINE': SCHEMES['sqlite'],
            'NAME': ':memory:',
        })

    # Parse the given URL.
    uri = urlparse.urlparse(url)

    # Update with environment configuration.
    config = DBConfig({
        'ENGINE': SCHEMES[uri.scheme],
        'NAME': urlparse.unquote(uri.path[1:] or ''),
        'USER': urlparse.unquote(uri.username or ''),
        'PASSWORD': urlparse.unquote(uri.password or ''),
        'HOST': uri.hostname or '',
        'PORT': str(uri.port or ''),
    })

    # Pass the query string into OPTIONS.
    options: Dict[str, Any] = {}
    qs = urlparse.parse_qs(uri.query)
    for key, values in qs.items():
        if key == 'isolation':
            options['isolation_level'] = {
                'uncommitted': 4,
                'serializable': 3,
                'repeatable': 2,
                'committed': 1,
                'autocommit': 0,
            }.get(values[-1], None)
            continue
        if key == 'search_path':
            options['options'] = f'-c search_path={values[-1]}'
            continue
        if key in ('autocommit', 'atomic_requests'):
            config[key.upper()] = is_truthy(values[-1])
            continue
        if key == 'conn_max_age':
            config['CONN_MAX_AGE'] = int(values[-1])
            continue
        options[key] = values[-1]

    if options:
        config['OPTIONS'] = options

    return config


__all__ = ['DBConfig', 'add_scheme', 'parse']
