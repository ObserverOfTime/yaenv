Usage
=====

Read dotenv file
----------------

.. code:: python

   from yaenv.core import Env
   env = Env('.env')

Access variables
----------------

.. code:: python

   password = env['PASSWORD']
   username = env.get('USERNAME', default='user')

Set variables
-------------

.. code:: python

   env['EMAIL'] = 'user@example.com'

Unset variables
---------------

.. code:: python

   del env['EMAIL']

Interpolation
-------------

.. code:: sh

   # POSIX variable expansion is supported
   DOMAIN=example.com
   EMAIL=user@${DOMAIN}

Type casting
------------

.. code:: python

   env.str('STR_VAR', default='')
   env.bool('BOOL_VAR', default=True)
   env.int('INT_VAR', default=5)
   env.float('FLOAT_VAR', default=0.5)
   env.list('LIST_VAR', default=[], separator=':')

Secret key
----------

.. code:: python

   # Generate a cryptographically secure
   # secret key if not already present
   secret = env.secret('SECRET_KEY')

And more
--------

.. code:: python

   # Get all the variables in the dotenv file
   env.dict()
   # Add the variables to os.environ
   env.set_as_environment_variables()
   # Access os.environ
   env.ENV
