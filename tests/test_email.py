from yaenv import email

class TestDB:
    """E-mail URL parser"""

    def test_parse_simple_email(self):
        """it can parse simple e-mail URLs"""
        _url = 'console://user:pass@127.0.0.1'
        _email = {
            'EMAIL_BACKEND': email.SCHEMES['console'],
            'EMAIL_HOST_USER': 'user',
            'EMAIL_HOST_PASSWORD': 'pass',
            'EMAIL_HOST': '127.0.0.1',
        }
        assert email.parse(_url) == _email
        _url = _url.replace('console', 'memory')
        _email['EMAIL_BACKEND'] = email.SCHEMES['memory']
        assert email.parse(_url) == _email
        _url = _url.replace('memory', 'dummy')
        _email['EMAIL_BACKEND'] = email.SCHEMES['dummy']
        assert email.parse(_url) == _email

    def test_parse_file_email(self):
        """it can parse file e-mail URLs"""
        _url = 'file://user:pass@127.0.0.1/email'
        _email = {
            'EMAIL_BACKEND': email.SCHEMES['file'],
            'EMAIL_HOST_USER': 'user',
            'EMAIL_HOST_PASSWORD': 'pass',
            'EMAIL_HOST': '127.0.0.1',
            'EMAIL_FILE_PATH': 'email',
        }
        assert email.parse(_url) == _email

    def test_parse_smtp_email(self):
        """it can parse SMTP e-mail URLs"""
        _url = 'smtp://user:pass@127.0.0.1'
        _email = {
            'EMAIL_BACKEND': email.SCHEMES['smtp'],
            'EMAIL_HOST_USER': 'user',
            'EMAIL_HOST_PASSWORD': 'pass',
            'EMAIL_HOST': '127.0.0.1',
            'EMAIL_PORT': 25,
        }
        assert email.parse(_url) == _email
        _url += ':2025'
        _email['EMAIL_PORT'] = 2025
        assert email.parse(_url) == _email

    def test_parse_smtp_tls_email(self):
        """it can parse SMTP (TLS) e-mail URLs"""
        _url = 'smtp+tls://user:pass@127.0.0.1'
        _email = {
            'EMAIL_BACKEND': email.SCHEMES['smtp'],
            'EMAIL_HOST_USER': 'user',
            'EMAIL_HOST_PASSWORD': 'pass',
            'EMAIL_HOST': '127.0.0.1',
            'EMAIL_PORT': 587,
            'EMAIL_USE_TLS': True,
        }
        assert email.parse(_url) == _email
        _url += ':2587'
        _email['EMAIL_PORT'] = 2587
        assert email.parse(_url) == _email
        _url = _url.replace('+tls', '').replace(':2', ':')
        _email['EMAIL_PORT'] = 587
        assert email.parse(_url) == _email

    def test_parse_smtp_ssl_email(self):
        """it can parse SMTP (SSL) e-mail URLs"""
        _url = 'smtp+ssl://user:pass@127.0.0.1'
        _email = {
            'EMAIL_BACKEND': email.SCHEMES['smtp'],
            'EMAIL_HOST_USER': 'user',
            'EMAIL_HOST_PASSWORD': 'pass',
            'EMAIL_HOST': '127.0.0.1',
            'EMAIL_PORT': 465,
            'EMAIL_USE_SSL': True,
        }
        assert email.parse(_url) == _email
        _url += ':2465'
        _email['EMAIL_PORT'] = 2465
        assert email.parse(_url) == _email
        _url = _url.replace('+ssl', '').replace(':2', ':')
        _email['EMAIL_PORT'] = 465
        assert email.parse(_url) == _email

    def test_parse_queryset(self):
        """it can parse queryset options"""
        _url = (
            'smtp+ssl://user:pass@127.0.0.1'
            '?certfile=cert&keyfile=key'
            '&timeout=1000&localtime=off'
        )
        _email = {
            'EMAIL_BACKEND': email.SCHEMES['smtp'],
            'EMAIL_HOST_USER': 'user',
            'EMAIL_HOST_PASSWORD': 'pass',
            'EMAIL_HOST': '127.0.0.1',
            'EMAIL_PORT': 465,
            'EMAIL_USE_SSL': True,
            'EMAIL_SSL_CERTFILE': 'cert',
            'EMAIL_SSL_KEYFILE': 'key',
            'EMAIL_TIMEOUT': 1000,
            'EMAIL_USE_LOCALTIME': False,
        }
        assert email.parse(_url) == _email
        _url = _url.replace('+ssl', '') + '&ssl=1'
        _email['EMAIL_PORT'] = 25
        assert email.parse(_url) == _email
        del _email['EMAIL_USE_SSL']
        _email['EMAIL_USE_TLS'] = True
        _url = _url.replace('ssl', 'tls')
        assert email.parse(_url) == _email
