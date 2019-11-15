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

   # raises EnvError if missing
   password = env['PASSWORD']
   # returns 'user' if missing
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

   # Get the path of the dotenv file
   env.envfile

   # Get all the variables in the dotenv file
   env.vars

   # Check if a variable is in the file
   'EMAIL' in env

   # Get the number of variables in the file
   len(env)

   # Iterate over the variables in the file
   for key, val in env:
      print(f'{key}: {val}')

   # Add the variables to os.environ
   env.setenv()

   # Access os.environ
   env.ENV
