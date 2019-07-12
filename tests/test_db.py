from pytest import mark

from yaenv import db

@mark.describe('Test database URL parser')
class TestDB:

    @mark.it('it can parse database URLs')
    def test_parse_database(self):
        _url = 'mysql://user:pass@127.0.0.1:3306/db'
        _db = {
            'ENGINE': db.SCHEMES['mysql'],
            'NAME': 'db',
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
        assert db.parse(_url) == _db
        _url = _url.replace('mysql', 'oracle').replace('3306', '1521')
        _db.update({'ENGINE': db.SCHEMES['oracle'], 'PORT': '1521'})
        assert db.parse(_url) == _db
        _url = _url.replace('oracle', 'pgsql').replace('1521', '5432')
        _db.update({'ENGINE': db.SCHEMES['pgsql'], 'PORT': '5432'})
        assert db.parse(_url) == _db

    @mark.it('it can parse in-memory SQLite database')
    def test_parse_sqlite_memory(self):
        _db = {
            'ENGINE': db.SCHEMES['sqlite'],
            'NAME': ':memory:'
        }
        assert db.parse('sqlite://:memory:') == _db

    @mark.it('it can parse relative SQLite database path')
    def test_parse_sqlite_relative(self):
        _db = {
            'ENGINE': db.SCHEMES['sqlite'],
            'NAME': 'db.sqlite3',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
        assert db.parse('sqlite:///db.sqlite3') == _db

    @mark.it('it can parse absolute SQLite database path')
    def test_parse_sqlite_absolute(self):
        _db = {
            'ENGINE': db.SCHEMES['sqlite'],
            'NAME': '/tmp/db.sqlite3',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
        assert db.parse('sqlite:////tmp/db.sqlite3') == _db

    @mark.it('it can parse queryset options')
    def test_parse_queryset(self):
        _url = 'pgsql://user:pass@127.0.0.1:5432/db'
        _url += '?isolation=committed&search_path=db'
        _url += '&autocommit=yes&atomic_requests=off'
        _url += '&conn_max_age=1000'
        _db = {
            'ENGINE': db.SCHEMES['pgsql'],
            'NAME': 'db',
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'OPTIONS': {
                'isolation_level': 1,
                'options': '-c search_path=db',
            },
            'AUTOCOMMIT': True,
            'ATOMIC_REQUESTS': False,
            'CONN_MAX_AGE': 1000,
        }
        assert db.parse(_url) == _db

    @mark.it('it can add custom schemes')
    def test_add_scheme(self):
        _scheme = 'spatialite'
        _engine = 'django.contrib.gis.db.backends.spatialite'
        db.add_scheme(_scheme, _engine)
        assert db.SCHEMES[_scheme] == _engine
        assert _scheme in db.urlparse.uses_netloc
        del db.SCHEMES[_scheme]
        db.urlparse.uses_netloc.remove(_scheme)
