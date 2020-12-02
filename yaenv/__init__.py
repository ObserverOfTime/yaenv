"""Yet another dotenv parser for Python."""

from importlib.metadata import version

from .core import Env, EnvError

__version__ = version(__name__)

__all__ = ['Env', 'EnvError']
