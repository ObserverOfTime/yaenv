"""Environment variable parser."""

from os import environ
from random import SystemRandom
from typing import Iterator, List, Optional

from dotenv.main import DotEnv, set_key, unset_key

from . import db, email, utils


class EnvError(Exception):
    """Exception class representing a dotenv error."""


class Env(DotEnv, object):
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

    Examples
    --------
    >>> open('.env').read()
    STR_VAR=value
    LIST_VAR=item1:item2
    SECRET_KEY=notsosecret
    >>> env = Env('.env')
    """

    def __init__(self, dotenv_path):
        # type: (str) -> None
        super(Env, self).__init__(dotenv_path)
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
        value = self.dict().get(key)
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
        self.dict()[key] = value
        set_key(self.dotenv_path, key, value)

    def __delitem__(self, key):
        # type: (str) -> None
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
            del self.dict()[key]
        except KeyError:
            error = "Missing environment variable: '{}'"
            raise EnvError(error.format(key))
        else:
            unset_key(self.dotenv_path, key)

    def __iter__(self):
        # type: () -> Iterator
        """
        Iterate through the entries in the dotenv file.

        Returns
        -------
        Iterator
            An iterator of key-value pairs.
        """
        return (entry for entry in utils.iteritems(self.dict()))

    def __contains__(self, item):
        # type: (str) -> bool
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
        return item in self.dict()

    def __len__(self):
        # type: () -> int
        """
        Return the number of environment variables.

        Returns
        -------
        int
            The number of variables defined in the dotenv file.
        """
        return len(self.dict())

    def __fspath__(self):
        # type: () -> str
        """
        Return the file system representation of the path.

        This method is used by :os:`fspath` (Python 3.6+).

        Returns
        -------
        str
            The path of the dotenv file.
        """
        return self.dotenv_path

    def __str__(self):
        # type: () -> str
        """
        Return a string representing the environment variables.

        Returns
        -------
        str
            The key-value pairs defined in the dotenv file as lines.
        """
        return '\n'.join(map('{0[0]}="{0[1]}"'.format, self))

    def __repr__(self):
        # type: () -> str
        """
        Return a string representing the object.

        Returns
        -------
        str
            A string that shows the path of the dotenv file.
        """
        return "Env('{}')".format(self.dotenv_path)

    def get(self, key, default=None):
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
        >>> env.get('STR_VAR', 'default')
        'value'
        """
        return self.ENV.get(key, self.dict().get(key) or default)

    def bool(self, key, default=None):
        # type: (str, Optional[bool]) -> Optional[bool]
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

    def int(self, key, default=None):
        # type: (str, Optional[int]) -> Optional[int]
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

    def float(self, key, default=None):
        # type: (str, Optional[float]) -> Optional[float]
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

    def list(self, key, default=None, separator=','):
        # type: (str, Optional[List], str) -> Optional[List]
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

    def db(self, key, default=None):
        # type: (str, Optional[str]) -> Optional[db.DBConfig]
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

    def email(self, key, default=None):
        # type: (str, Optional[str]) -> Optional[email.EmailConfig]
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
