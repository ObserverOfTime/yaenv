from sys import version_info

import pytest

import yaenv


@pytest.fixture
def env():
    """Environment parser object."""
    return yaenv.Env('tests/.env')


@pytest.mark.describe('Test .env file parser')
class TestEnv:

    @pytest.mark.it('it can get environment variables')
    def test_getitem(self, env: yaenv.Env):
        assert env['BLANK'] == ''
        assert env['DOMAIN'] == 'example.com'

    @pytest.mark.it('it can set environment variables')
    def test_setitem(self, env: yaenv.Env):
        env['NEW_VAR'] = 'new_var'
        assert env['NEW_VAR'] == 'new_var'

    @pytest.mark.it('it can unset environment variables')
    def test_delitem(self, env: yaenv.Env):
        assert 'NEW_VAR' in env
        del env['NEW_VAR']
        assert 'NEW_VAR' not in env
        with pytest.raises(yaenv.EnvError) as err:
            del env['NEW_VAR']
        assert 'Missing' in str(err.value)

    @pytest.mark.it('it can iterate over key-value pairs')
    def test_iter(self, env: yaenv.Env):
        for key, val in env:
            assert env[key] == val

    @pytest.mark.it('it can interpolate variables')
    def test_interpolation(self, env: yaenv.Env):
        assert env['EMAIL'] == 'user@' + env['DOMAIN']

    @pytest.mark.it('it can update os.environ')
    def test_setenv(self, env: yaenv.Env):
        from os import environ
        assert 'EMAIL' not in environ
        env.setenv()
        assert 'EMAIL' in environ

    @pytest.mark.skipif(version_info < (3, 6), reason='requires Python 3.6+')
    @pytest.mark.it('it returns the file system path of the dotenv file')
    def test_fspath(self, env: yaenv.Env):
        from os import fspath
        from filecmp import cmp
        assert fspath(env) == 'tests/.env'
        assert cmp(env, 'tests/.env')

    @pytest.mark.it('it returns default values for optional variables')
    def test_get(self, env: yaenv.Env):
        assert env.get('BLANK', 'default') == ''
        assert env.get('MISSING') is None
        assert env.get('MISSING', 'default') == 'default'

    @pytest.mark.it('it raises EnvError for missing required variables')
    def test_getitem_missing(self, env: yaenv.Env):
        with pytest.raises(yaenv.EnvError) as err:
            _ = env['MISSING']
        assert 'Missing' in str(err.value)

    @pytest.mark.it('it raises EnvError for an invalid dotenv file')
    def test_invalid_envfile(self):
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.Env('/invalidfile')
        assert 'does not exist' in str(err.value)


@pytest.mark.describe('Test type-casting')
class TestEnvCasting:

    @pytest.mark.it('it can cast to bool')
    def test_bool(self, env: yaenv.Env):
        _val = env.bool('BOOL_VAR')
        assert not _val and type(_val) == bool
        _val = env.bool('INT_VAR')
        assert _val and type(_val) == bool
        _val = env.bool('MISSING', True)
        assert _val and type(_val) == bool
        with pytest.raises(yaenv.EnvError) as err:
            _ = env.bool('FLOAT_VAR')
        assert 'Invalid boolean' in str(err.value)
        assert env.bool('MISSING') is None

    @pytest.mark.it('it can cast to int')
    def test_int(self, env: yaenv.Env):
        _val = env.int('INT_VAR')
        assert _val == 1 and type(_val) == int
        _val = env.int('MISSING', -2)
        assert _val == -2 and type(_val) == int
        with pytest.raises(yaenv.EnvError) as err:
            _ = env.int('LIST_VAR')
        assert 'Invalid integer' in str(err.value)
        assert env.int('MISSING') is None

    @pytest.mark.it('it can cast to float')
    def test_float(self, env: yaenv.Env):
        _val = env.float('FLOAT_VAR')
        assert _val == 10.0 and type(_val) == float
        _val = env.float('MISSING', -3.1)
        assert _val == -3.1 and type(_val) == float
        with pytest.raises(yaenv.EnvError) as err:
            _ = env.float('LIST_VAR')
        assert 'Invalid numerical' in str(err.value)
        assert env.float('MISSING') is None

    @pytest.mark.it('it can cast to list')
    def test_list(self, env: yaenv.Env):
        _val = env.list('LIST_VAR', separator=':')
        _expect = ['item1', 'item2']
        assert _val == _expect and type(_val) == list
        _expect.append('item3')
        _val = env.list('MISSING', _expect)
        assert _val == _expect and type(_val) == list
        assert env.list('MISSING') is None


@pytest.mark.describe('Test Django integration')
class TestEnvDjango:

    @pytest.mark.it('it can parse database URLs')
    def test_db(self, env: yaenv.Env):
        _db = {
            'ENGINE': yaenv.db.SCHEMES['sqlite'],
            'NAME': 'db.sqlite3',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
        assert env.db('DB_URL') == _db
        _db = {
            'ENGINE': yaenv.db.SCHEMES['sqlite'],
            'NAME': ':memory:',
        }
        assert env.db('DB_URL_DEFAULT', 'sqlite://:memory:') == _db
        with pytest.raises(yaenv.EnvError) as err:
            _ = env.db('INVALID_URL', 'invalid')
        assert 'Invalid database' in str(err.value)
        assert env.db('MISSING') is None

    @pytest.mark.it('it can parse e-mail URLs')
    def test_email(self, env: yaenv.Env):
        _email = {
            'EMAIL_BACKEND': yaenv.email.SCHEMES['dummy'],
            'EMAIL_HOST_USER': '',
            'EMAIL_HOST_PASSWORD': '',
            'EMAIL_HOST': 'localhost'
        }
        assert env.email('EMAIL_URL') == _email
        _email.update({
            'EMAIL_BACKEND': yaenv.email.SCHEMES['console'],
            'EMAIL_HOST': '127.0.0.1'
        })
        assert env.email('EMAIL_URL_MISSING', 'console://127.0.0.1') == _email
        with pytest.raises(yaenv.EnvError) as err:
            _ = env.email('INVALID_URL', 'invalid')
        assert 'Invalid e-mail' in str(err.value)
        assert env.email('MISSING') is None

    @pytest.mark.it('it can get and generate secret keys')
    def test_secret(self, env: yaenv.Env):
        assert env.secret() == 'notsosecret'
        assert 'NEW_SECRET_KEY' not in env
        _secret = env.secret('NEW_SECRET_KEY')
        assert _secret is not None
        assert _secret != env.secret('NEW_SECRET_KEY2')
        del env['NEW_SECRET_KEY'], env['NEW_SECRET_KEY2']


@pytest.mark.describe('Test line parser')
class TestEnvVar:

    @pytest.mark.it('it can parse unquoted variables')
    def test_unquoted(self):
        e = yaenv.core.EnvVar('key=value\n')
        assert e.key == 'key'
        assert e.value == 'value'
        assert e._interpolate

    @pytest.mark.it('it can parse double-quoted variables')
    def test_double_quoted(self):
        e = yaenv.core.EnvVar('key="value"\n')
        assert e.key == 'key'
        assert e.value == 'value'
        assert e._interpolate

    @pytest.mark.it('it can parse single-quoted variables')
    def test_single_quoted(self):
        e = yaenv.core.EnvVar("key='value'\n")
        assert e.key == 'key'
        assert e.value == 'value'
        assert not e._interpolate

    @pytest.mark.it('it can parse blank variables')
    def test_blank(self):
        assert yaenv.core.EnvVar('key=').value == ''
        assert yaenv.core.EnvVar('key=""').value == ''
        assert yaenv.core.EnvVar("key=''").value == ''
        assert yaenv.core.EnvVar('key= ').value == ''

    @pytest.mark.it('it ignores blank lines')
    def test_blank(self):
        assert yaenv.core.EnvVar('\n') is None
        assert yaenv.core.EnvVar(' \t ') is None
        assert yaenv.core.EnvVar('# comment') is None

    @pytest.mark.it('it raises EnvError for invalid keys')
    def test_invalid_key(self):
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar('221b="starts with number"')
        assert 'Invalid key' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar('_="not assignable"')
        assert 'Invalid key' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar('o-o="invalid character"')
        assert 'Invalid key' in str(err.value)

    @pytest.mark.it('it raises EnvError for mismatched quotes')
    def test_mismatched_quote(self):
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar('double="missing-closing')
        assert 'Mismatched quotes' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar('double=missing-opening"')
        assert 'Mismatched quotes' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar("single='missing-closing")
        assert 'Mismatched quotes' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar("single=missing-opening'")
        assert 'Mismatched quotes' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar("both=\"mismatched'")
        assert 'Mismatched quotes' in str(err.value)
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar("both='mismatched\"")
        assert 'Mismatched quotes' in str(err.value)

    @pytest.mark.it('it raises EnvError for surplus tokens')
    def test_surplus_token(self):
        with pytest.raises(yaenv.EnvError) as err:
            _ = yaenv.core.EnvVar('surplus=this must be quoted')
        assert 'Surplus token' in str(err.value)