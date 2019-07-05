"""E-mail URL parser."""

from typing import Any, Dict, NewType

from .utils import is_truthy, urlparse

EmailConfig = NewType('EmailConfig', Dict[str, Any])

# Supported schemes.
SCHEMES = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
    'file': 'django.core.mail.backends.filebased.EmailBackend',
    'memory': 'django.core.mail.backends.locmem.EmailBackend',
    'dummy': 'django.core.mail.backends.dummy.EmailBackend'
}  # type: Dict[str, str]

# Scheme aliases.
SCHEMES['smtp+tls'] = SCHEMES['smtp']
SCHEMES['smtp+ssl'] = SCHEMES['smtp']

# Register e-mail schemes in URLs.
urlparse.uses_netloc += list(SCHEMES)


def parse(url):
    # type: (str) -> EmailConfig
    """
    Parse an e-mail URL.

    Parameters
    ----------
    url : str
        The e-mail URL to be parsed.

    Returns
    -------
    EmailConfig
        A dictionary that can be used in
        :django:`django.settings.EMAIL_* <email-backend>`.

    Examples
    --------
    >>> parse('smtp+tls://user:pass@example.com')
    {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST_USER': 'user',
        'EMAIL_HOST_PASSWORD': 'pass',
        'EMAIL_HOST': 'example.com',
        'EMAIL_USE_TLS': True,
        'EMAIL_PORT': 587
    }
    """
    # Parse the given URL.
    uri = urlparse.urlparse(url)

    # Update with environment configuration
    config = EmailConfig({
        'EMAIL_BACKEND': SCHEMES[uri.scheme],
        'EMAIL_HOST_USER': urlparse.unquote(uri.username or ''),
        'EMAIL_HOST_PASSWORD': urlparse.unquote(uri.password or ''),
        'EMAIL_HOST': uri.hostname or 'localhost',
    })

    # Set config for file.
    if uri.scheme == 'file':
        config['EMAIL_FILE_PATH'] = uri.path[1:]

    # Set config for smtp.
    if uri.scheme == 'smtp':
        config['EMAIL_PORT'] = uri.port or 25

    # Set config for smtp+tls.
    if uri.scheme == 'smtp+tls':
        config['EMAIL_USE_TLS'] = True
        config['EMAIL_PORT'] = uri.port or 587

    # Set config for smtp+ssl.
    if uri.scheme == 'smtp+ssl':
        config['EMAIL_USE_SSL'] = True
        config['EMAIL_PORT'] = uri.port or 465

    # Set extra config from the query string.
    for key, values in urlparse.parse_qs(uri.query):
        if key == 'certfile':
            config['EMAIL_SSL_CERTFILE'] = values[-1]
        if key == 'keyfile':
            config['EMAIL_SSL_KEYFILE'] = values[-1]
        if key == 'timeout':
            config['EMAIL_TIMEOUT'] = int(values[-1])
        if key == 'localtime':
            config['EMAIL_USE_LOCALTIME'] = is_truthy(values[-1])

    return config


__all__ = ['EmailConfig', 'parse']
