"""Environment variable parser."""

from os import environ
from random import SystemRandom
from typing import List, Optional

from dotenv.main import DotEnv, set_key, unset_key

from . import db, email, utils


class EnvError(Exception):
    """Exception class representing a dotenv error."""


class Env(DotEnv):
    """
    Class used to parse and access environment variables.

    Attributes
    ----------
    ENV : os._Environ
        A reference to :os:`environ`.

    Parameters
    ----------
    dotenv_path : str
        The path to a ``.env`` file.

    Methods
    -------
    get(key, default=None)
        Alias for :meth:`str`.

    Examples
    --------
    >>> open('.env').read()
    STR_VAR=value
    LIST_VAR=item1:item2
    SECRET_KEY=notsosecret
    >>> env = Env('.env')
    >>> env.get('STR_VAR')
    value
    """

    def __init__(self, dotenv_path):
        # type: (str) -> None
        super(Env, self).__init__(dotenv_path)
        self.get = self.str
        self.ENV = environ

    def __getitem__(self, key):
        # type: (str) -> str
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
        value = super(Env, self).get(key)
        if value is None:
            error = "Missing environment variable: '{}'"
            raise EnvError(error.format(key))
        return value

    def __setitem__(self, key, value):
        # type: (str, str) -> None
        """
        Set an environment variable.

        Parameters
        ----------
        key : str
            The name of the variable.
        value : str
            The value of the variable as ``str``.
        """
        set_key(self.dotenv_path, key, value)

    def __delitem__(self, key):
        # type: (str) -> None
        """
        Unset an environment variable.

        Parameters
        ----------
        key : str
            The name of the variable.
        """
        unset_key(self.dotenv_path, key)

    def str(self, key, default=None):
        # type: (str, Optional[str]) -> Optional[str]
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
        >>> env.str('STR_VAR', 'default')
        value
        """
        return super(Env, self).get(key) or default

    def bool(self, key, default=None):
        # type: (str, Optional[bool]) -> bool
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
        if isinstance(value, bool):
            return value
        if utils.is_truthy(value):
            return True
        if utils.is_falsy(value):
            return False
        raise EnvError("Invalid boolean value: '{}'".format(value))

    def int(self, key, default=None):
        # type: (str, Optional[int]) -> int
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
        try:
            return int(value)
        except ValueError:
            raise EnvError("Invalid integer value: '{}'".format(value))

    def float(self, key, default=None):
        # type: (str, Optional[float]) -> float
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
        try:
            return float(value)
        except ValueError:
            raise EnvError("Invalid numerical value: '{}'".format(value))

    def list(self, key, default=None, separator=','):
        # type: (str, Optional[List], str) -> List
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
        if isinstance(value, List):
            return value
        return value.split(separator)

    def db(self, key, default=None):
        # type: (str, Optional[str]) -> db.DBConfig
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
        db.DBConfig
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
        try:
            return db.parse(value)
        except Exception:
            raise EnvError("Invalid database URL: '{}'".format(value))

    def email(self, key, default=None):
        # type: (str, Optional[str]) -> email.EmailConfig
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
        email.EmailConfig
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
        try:
            return email.parse(value)
        except Exception:
            raise EnvError("Invalid e-mail URL: '{}'".format(value))

    def secret(self, key='SECRET_KEY'):
        # type: (str) -> str
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


__all__ = ['Env', 'EnvError']
