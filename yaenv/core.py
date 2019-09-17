"""Environment variable parser."""

from functools import lru_cache
from os import environ, path
from random import SystemRandom
from re import compile as regex
from shlex import shlex
from shutil import move
from tempfile import mkstemp
from typing import Dict, Iterator, List, Tuple, Optional

from . import db, email, utils


class EnvError(Exception):
    """Exception class representing a dotenv error."""


class EnvVar:
    """
    Class that represents an environment variable.

    Attributes
    ----------
    key : str
        The key of the variable.
    value : str
        The value of the variable.
    """

    def __new__(cls, line: str):
        """
        Parse a line and return a new instance or ``None``.

        Parameters
        ----------
        line : str
            The line to be parsed.

        Returns
        -------
        Optional[EnvVar]
            Returns a new ``EnvVar`` if all went well, or ``None``
            if the line doesn't contain a variable declaration.

        Raises
        ------
        EnvError
            If the line cannot be parsed.

        Examples
        --------
        >>> print(repr(EnvVar('example=???')))
        EnvVar('example', '???')
        >>> print(repr(EnvVar('# comment')))
        None
        """
        lex = shlex(line)

        key = lex.read_token()
        if not key:
            return None

        # invalid key
        if (
            not all(c in lex.wordchars for c in key)
            or not lex.get_token() == '='
            or key == '_' or key[0] in '0123456789'
        ):
            error = 'Invalid key in line: {}'
            raise EnvError(error.format(line))

        lex.whitespace_split = True
        try:
            value = lex.read_token()
        except ValueError:
            error = 'Mismatched quotes in line: {}'
            raise EnvError(error.format(line))

        # surplus token after value
        if lex.read_token():
            error = 'Surplus token in line: {}'
            raise EnvError(error.format(line))

        instance = super(EnvVar, cls).__new__(cls)
        instance.key = key

        # blank value
        if value == '':
            instance.value = value
            instance._interpolate = False
            return instance

        # double-quoted value
        if value[0] == '"' or value[-1] == '"':
            if not value[0] == value[-1]:
                error = 'Mismatched quotes in line: {}'
                raise EnvError(error.format(line))
            instance.value = value[1:-1]
            instance._interpolate = True
            return instance

        # single-quoted value
        if value[0] == "'" or value[-1] == "'":
            if not value[0] == value[-1]:
                error = 'Mismatched quotes in line: {}'
                raise EnvError(error.format(line))
            instance.value = value[1:-1]
            instance._interpolate = False
            return instance

        instance.value = value
        instance._interpolate = True
        return instance

    def __bool__(self) -> bool:
        """
        Return whether the variable can be interpolated or not.

        Returns
        -------
        bool
            ``True`` unless the value is blank or enclosed in single quotes.
        """
        return self._interpolate

    def __iter__(self) -> Iterator[str]:
        """
        Iterate through the tokens of the variable.

        Returns
        -------
        Iterator[str]
            An iterator containing the key and value.
        """
        yield from (self.key, self.value)

    def __str__(self) -> str:
        """
        Return the variable as a string.

        Returns
        -------
        str
            The value of the variable.
        """
        return self.value

    def __repr__(self) -> str:
        """
        Return a string representing the object.

        Returns
        -------
        str
            A string that shows the key and value of the variable.
        """
        return "EnvVar('{0.key}', '{0.value}')".format(self)


class Env:
    """
    Class used to parse dotenv files and access their variables.

    Attributes
    ----------
    ENV : os._Environ
        A reference to :os:`environ`.
    envfile : str
        The dotenv file of the object.

    Parameters
    ----------
    envfile : str
        The path to a dotenv file.

    Examples
    --------
    >>> print(open('.env').read())
    STR_VAR=value
    LIST_VAR=item1:item2
    SECRET_KEY=notsosecret
    >>> env = Env('.env')
    """

    def __init__(self, envfile: str) -> None:
        if not path.isfile(envfile):
            error = "File '{}' does not exist"
            raise EnvError(error.format(envfile))

        self.envfile = envfile
        self.ENV = environ

    def __getitem__(self, key: str) -> str:
        """
        Return an environment variable that cannot be missing.

        Parameters
        ----------
        key : str
            The name of the variable.

        Returns
        -------
        str
            The value of the variable as ``str``.

        Raises
        ------
        EnvError
            If the environment variable is missing.
        """
        value = self.vars.get(key)
        if value is None:
            error = "Missing environment variable: '{}'"
            raise EnvError(error.format(key))
        return value

    def __setitem__(self, key: str, value: str) -> None:
        """
        Set an environment variable.

        Parameters
        ----------
        key : str
            The name of the variable.
        value : str
            The value of the variable as ``str``.
        """
        self.vars[key] = value
        self._replace(key, value)

    def __delitem__(self, key: str) -> None:
        """
        Unset an environment variable.

        Parameters
        ----------
        key : str
            The name of the variable.

        Raises
        ------
        EnvError
            If the variable is not set.
        """
        try:
            del self.vars[key]
        except KeyError:
            error = "Missing environment variable: '{}'"
            raise EnvError(error.format(key))
        else:
            self._replace(key, None)

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        """
        Iterate through the entries in the dotenv file.

        Returns
        -------
        Iterator[Tuple[str, str]]
            An iterator of key-value pairs.
        """
        yield from self.vars.items()

    def __contains__(self, item: str) -> bool:
        """
        Check whether a variable is defined in the dotenv file.

        Parameters
        ----------
        item : str
            The name of the variable.

        Returns
        -------
        bool
            ``True`` if the item is defined in the dotenv file.
        """
        return item in self.vars

    def __len__(self) -> int:
        """
        Return the number of environment variables.

        Returns
        -------
        int
            The number of variables defined in the dotenv file.
        """
        return len(self.vars)

    def __fspath__(self) -> str:
        """
        Return the file system representation of the path.

        This method is used by :os:`fspath` (Python 3.6+).

        Returns
        -------
        str
            The path of the dotenv file.
        """
        return self.envfile

    def __str__(self) -> str:
        """
        Return a string representing the environment variables.

        Returns
        -------
        str
            The key-value pairs defined in the dotenv file as lines.
        """
        return '\n'.join(map('{0[0]}="{0[1]}"'.format, self))

    def __repr__(self) -> str:
        """
        Return a string representing the object.

        Returns
        -------
        str
            A string that shows the path of the dotenv file.
        """
        return "Env('{}')".format(self.envfile)

    @property
    @lru_cache()
    def vars(self) -> Dict[str, str]:
        """`Dict[str, str]` : Get the environment variables as a ``dict``."""
        def _sub_callback(match):
            return {**environ, **result}.get(match.group(1), '')

        with open(self.envfile, 'r') as f:
            envvars = list(filter(None.__ne__, map(EnvVar, f.readlines())))
            result = dict(envvars)

        # substitute variables that can be interpolated
        posix = regex(r'\$\{([^}].*)?\}')
        for var in filter(bool, envvars):
            result[var.key] = posix.sub(_sub_callback, var.value)

        return result

    def setenv(self) -> None:
        """Add the variables defined in the dotenv file to :os:`environ`."""
        self.ENV.update(self.vars)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Return an environment variable or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[str]
            The default value.

        Returns
        -------
        Optional[str]
            The value of the variable or the ``default`` value.

        Examples
        --------
        >>> env.get('STR_VAR', 'default')
        'value'
        """
        return self.ENV.get(key, self.vars.get(key) or default)

    def bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """
        Return an environment variable as a ``bool``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[bool]
            The default value.

        Returns
        -------
        Optional[bool]
            The ``bool`` value of the variable or the ``default`` value.

        Raises
        ------
        EnvError
            If the variable cannot be cast to ``bool``.

        Examples
        --------
        >>> env.bool('BOOL_VAR', False)
        False
        """
        value = self.get(key, default)
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if utils.is_truthy(value):
            return True
        if utils.is_falsy(value):
            return False
        raise EnvError("Invalid boolean value: '{}'".format(value))

    def int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """
        Return an environment variable as an ``int``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[int]
            The default value.

        Returns
        -------
        Optional[int]
            The ``int`` value of the variable or the ``default`` value.

        Raises
        ------
        EnvError
            If the variable cannot be cast to ``int``.

        Examples
        --------
        >>> env.int('INT_VAR', 10)
        10
        """
        value = self.get(key, default)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            raise EnvError("Invalid integer value: '{}'".format(value))

    def float(self, key: str, default:
              Optional[float] = None) -> Optional[float]:
        """
        Return an environment variable as a ``float``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[float]
            The default value.

        Returns
        -------
        Optional[float]
            The ``float`` value of the variable or the ``default`` value.

        Raises
        ------
        EnvError
            If the variable cannot be cast to ``float``.

        Examples
        --------
        >>> env.float('FLOAT_VAR', 0.3)
        0.3
        """
        value = self.get(key, default)
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            raise EnvError("Invalid numerical value: '{}'".format(value))

    def list(self, key: str, default: Optional[List] = None,
             separator: str = ',') -> Optional[List]:
        """
        Return an environment variable as a ``list``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[List]
            The default value.
        separator : str
            The separator to use when splitting the list.

        Returns
        -------
        Optional[List]
            The ``list`` value of the variable or the ``default`` value.

        Examples
        --------
        >>> env.list('LIST_VAR', separator=':')
        ['item1', 'item2']
        """
        value = self.get(key, default)
        if value is None:
            return None
        if isinstance(value, List):
            return value
        return value.split(separator)

    def db(self, key: str, default:
           Optional[str] = None) -> Optional[db.DBConfig]:
        """
        Return a dictionary that can be used for Django's database settings.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[str]
            The default (unparsed) value.

        Returns
        -------
        Optional[db.DBConfig]
            A database config object for Django.

        Raises
        ------
        EnvError
            If the variable cannot be parsed.

        See Also
        --------
        :meth:`yaenv.db.parse` : Database URL parser.
        """
        value = self.get(key, default)
        if value is None:
            return None
        try:
            return db.parse(value)
        except Exception:
            raise EnvError("Invalid database URL: '{}'".format(value))

    def email(self, key: str, default:
              Optional[str] = None) -> Optional[email.EmailConfig]:
        """
        Return a dictionary that can be used for Django's e-mail settings.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : Optional[str]
            The default (unparsed) value.

        Returns
        -------
        Optional[email.EmailConfig]
            An e-mail config object for Django.

        Raises
        ------
        EnvError
            If the variable cannot be parsed.

        See Also
        --------
        :meth:`yaenv.email.parse` : E-mail URL parser.
        """
        value = self.get(key, default)
        if value is None:
            return None
        try:
            return email.parse(value)
        except Exception:
            raise EnvError("Invalid e-mail URL: '{}'".format(value))

    def secret(self, key: str = 'SECRET_KEY') -> str:
        """
        Return a cryptographically secure secret key.

        If the key is empty, it is generated and saved.

        Parameters
        ----------
        key : str
            The name of the key.

        Returns
        -------
        str
            A random string.
        """
        value = self.get(key)
        if not value:
            random = SystemRandom().choice
            value = ''.join(random(
                'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            ) for _ in range(50))
            self[key] = value
        return value

    def _replace(self, key: str, value: Optional[str]) -> None:
        target = mkstemp(prefix='yaenv')[-1]
        pattern = regex(r'^\s*{}\s*='.format(key))
        replaced = value is None  # can't replace if there's no value

        if value is not None:
            value = value.replace('"', '\\"') \
                .replace('\n', '\\n').replace('\t', '\\t')
            newline = '{}="{}"\n'.format(key, value)

        with open(target, 'w') as tf, open(self.envfile, 'r') as sf:
            for line in sf:
                if not pattern.match(line):
                    tf.write(line)
                elif value is not None:
                    tf.write(newline)
                    replaced = True
            if not replaced:
                if not line[-1] == '\n':
                    tf.write('\n')  # ensure new line
                tf.write(newline)

        move(target, self.envfile)


__all__ = ['Env', 'EnvError', 'EnvVar']
