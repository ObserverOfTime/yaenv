"""Environment variable parser."""

from __future__ import annotations

from functools import cached_property
from os import PathLike, environ, fspath, path
from re import compile as regex
from secrets import token_urlsafe
from shlex import shlex
from shutil import move
from tempfile import mkstemp
from typing import Iterator, Literal

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

    _interpolate: bool
    key: str
    value: str

    def __new__(cls, line: str) -> EnvVar | None:  # type: ignore
        """
        Parse a line and return a new instance or ``None``.

        Parameters
        ----------
        line : str
            The line to be parsed.

        Returns
        -------
        EnvVar | None
            A new ``EnvVar`` if all went well, or ``None`` if
            the line doesn't contain a variable declaration.

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
            or lex.get_token() != '='
            or key == '_' or key[0] in '0123456789'
        ):
            raise EnvError(f'Invalid key in line: {line}')

        lex.whitespace_split = True
        try:
            value = lex.read_token()
        except ValueError as e:
            raise EnvError(f'Mismatched quotes in line: {line}') from e

        # surplus token after value
        if lex.read_token():
            raise EnvError(f'Surplus token in line: {line}')

        instance = super(EnvVar, cls).__new__(cls)
        instance.key = key

        # blank value
        if not value:
            instance.value = ''
            instance._interpolate = False
            return instance

        # double-quoted value
        if value[0] == '"' or value[-1] == '"':
            if not value[0] == value[-1]:
                raise EnvError(f'Mismatched quotes in line: {line}')
            instance.value = value[1:-1]
            instance._interpolate = True
            return instance

        # single-quoted value
        if value[0] == "'" or value[-1] == "'":
            if not value[0] == value[-1]:
                raise EnvError(f'Mismatched quotes in line: {line}')
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
        yield self.key
        yield self.value

    def __len__(self) -> Literal[0, 1, 2]:
        """
        Return a number which represents the state of the ``EnvVar``.

        Returns
        -------
        Literal[0, 1, 2]
            ``0`` if the ``EnvVar`` is ``None``, ``1``
            if the value is blank, or ``2`` otherwise.
        """
        if self is None:
            return 0
        if not self.value:
            return 1
        return 2

    def __str__(self) -> str:  # pragma: no cover
        """
        Return the variable as a string.

        Returns
        -------
        str
            The value of the variable.
        """
        return self.value

    def __repr__(self) -> str:  # pragma: no cover
        """
        Return a string representing the object.

        Returns
        -------
        str
            A string that shows the key and value of the variable.
        """
        return f"EnvVar('{self.key}', '{self.value}')"


class Env(PathLike):
    """
    Class used to parse dotenv files and access their variables.

    Attributes
    ----------
    ENV : os._Environ
        A reference to :os:`environ`.
    envfile : str | :os:`PathLike`
        The dotenv file of the object.

    Parameters
    ----------
    envfile : str | :os:`PathLike`
        The path to a dotenv file.

    Examples
    --------
    >>> print(open('.env').read())
    STR_VAR=value
    LIST_VAR=item1:item2
    SECRET_KEY=notsosecret
    >>> env = Env('.env')
    """

    def __init__(self, envfile: str | PathLike) -> None:
        if not path.isfile(envfile):
            raise EnvError(f"File '{envfile}' does not exist")
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
            raise EnvError(f"Missing environment variable: '{key}'")
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
            raise EnvError(f"Missing environment variable: '{key}'")
        else:
            self._replace(key, None)

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """
        Iterate through the entries in the dotenv file.

        Returns
        -------
        Iterator[tuple[str, str]]
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
            ``True`` if the variable is defined.
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
        Return the file system representation of the object.

        This method is used by :os:`fspath`.

        Returns
        -------
        str
            The path of the dotenv file.
        """
        return fspath(self.envfile)

    def __str__(self) -> str:  # pragma: no cover
        """
        Return a string representing the environment variables.

        Returns
        -------
        str
            The key-value pairs defined in the dotenv file as lines.
        """
        return '\n'.join(f'{k}="{v}"' for k, v in self)

    def __repr__(self) -> str:  # pragma: no cover
        """
        Return a string representing the object.

        Returns
        -------
        str
            A string that shows the path of the dotenv file.
        """
        return f"Env('{self.envfile}')"

    @cached_property
    def vars(self) -> dict[str, str]:
        """`dict[str, str]` : Get the environment variables as a ``dict``."""
        def _sub_callback(match):  # type: ignore
            return (self.ENV | result).get(match.group(1), '')

        with open(self.envfile, 'r') as f:
            envvars = list(filter(EnvVar.__len__, map(EnvVar, f.readlines())))
            result = dict(envvars)  # type: ignore

        # substitute variables that can be interpolated
        posix = regex(r'\$\{([^}].*)?\}')
        for var in filter(bool, envvars):
            result[var.key] = posix.sub(_sub_callback, var.value)

        return result

    def setenv(self) -> None:
        """Add the variables defined in the dotenv file to :os:`environ`."""
        self.ENV |= self.vars  # type: ignore

    def get(self, key: str, default: str | None = None) -> str | None:
        """
        Return an environment variable or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : str | None
            The default value.

        Returns
        -------
        str | None
            The value of the variable or the ``default`` value.

        Examples
        --------
        >>> env.get('STR_VAR', 'default')
        'value'
        """
        return self.ENV.get(key, self.vars.get(key) or default)

    def bool(self, key: str, default: bool | None = None) -> bool | None:
        """
        Return an environment variable as a ``bool``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : bool | None
            The default value.

        Returns
        -------
        bool | None
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
        value = self.get(key)
        if value is None:
            return default
        if utils.is_truthy(value):
            return True
        if utils.is_falsy(value):
            return False
        raise EnvError(f"Invalid boolean value: '{value}'")

    def int(self, key: str, default: int | None = None) -> int | None:
        """
        Return an environment variable as an ``int``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : int | None
            The default value.

        Returns
        -------
        int | None
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
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise EnvError(f"Invalid integer value: '{value}'")

    def float(self, key: str, default: float | None = None) -> float | None:
        """
        Return an environment variable as a ``float``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : float | None
            The default value.

        Returns
        -------
        float | None
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
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise EnvError(f"Invalid numerical value: '{value}'")

    def list(self, key: str, default: list | None = None,
             separator: str = ',') -> list | None:
        """
        Return an environment variable as a ``list``, or a default value.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : list | None
            The default value.
        separator : str
            The separator to use when splitting the list.

        Returns
        -------
        list | None
            The ``list`` value of the variable or the ``default`` value.

        Examples
        --------
        >>> env.list('LIST_VAR', separator=':')
        ['item1', 'item2']
        """
        value = self.get(key)
        if value is None:
            return default
        return value.split(separator)

    def db(self, key: str, default: str | None = None) -> db.DBConfig | None:
        """
        Return a dictionary that can be used for Django's database settings.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : str | None
            The default (unparsed) value.

        Returns
        -------
        db.DBConfig | None
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
        except Exception as e:
            raise EnvError(f"Invalid database URL: '{value}'") from e

    def email(self, key: str, default: str | None
              = None) -> email.EmailConfig | None:
        """
        Return a dictionary that can be used for Django's e-mail settings.

        Parameters
        ----------
        key : str
            The name of the variable.
        default : str | None
            The default (unparsed) value.

        Returns
        -------
        email.EmailConfig | None
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
        except Exception as e:
            raise EnvError(f"Invalid e-mail URL: '{value}'") from e

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
            The value of the key or a random string.
        """
        value = self.get(key)
        if value is None:
            value = token_urlsafe(37)
            self[key] = value
        return value

    def _replace(self, key: str, value: str | None) -> None:
        target = mkstemp(prefix='yaenv')[-1]
        pattern = regex(fr'^\s*{key}\s*=')
        replaced = value is None  # can't replace if there's no value

        if value is not None:
            value = value.replace('"', '\\"') \
                .replace('\n', '\\n').replace('\t', '\\t')
            newline = f'{key}="{value}"\n'

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
