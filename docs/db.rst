Database
========

Format: ``{scheme}://{user}:{password}@{host}:{port}/{database}?{parameters}``

SQLite
------

SQLite accepts the following three formats:

* `in-memory database`_: ``sqlite://:memory:``
* relative path: ``sqlite:///db.sqlite3``
* absolute path: ``sqlite:////var/run/sqlite.db``

.. _in-memory database: https://www.sqlite.org/inmemorydb.html

Schemes
-------

* mysql: ``django.db.backends.mysql``
* oracle: ``django.db.backends.oracle``
* pgsql: ``django.db.backends.postgresql``
* postgres: ``django.db.backends.postgresql``
* postgresql: ``django.db.backends.postgresql``
* sqlite: ``django.db.backends.sqlite3``
* sqlite3: ``django.db.backends.sqlite3``

.. note::

   You can add more schemes with :func:`~yaenv.db.add_scheme`.

Parameters
----------

You can define database options as query parameters.

* conn_max_age: CONN_MAX_AGE_
* autocommit: AUTOCOMMIT_
* atomic_requests: ATOMIC_REQUESTS_
* search_path: `PostgreSQL search path`_
* isolation: `PostgreSQL isolation level`_
  (``uncommitted``/``serializable``/``repeatable``/``committed``/``autocommit``)

Other parameters will be passed to OPTIONS_ as is.

.. _CONN_MAX_AGE:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-CONN_MAX_AGE

.. _AUTOCOMMIT:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-AUTOCOMMIT

.. _ATOMIC_REQUESTS:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-ATOMIC_REQUESTS

.. _OPTIONS:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-OPTIONS

.. _PostgreSQL search path:
   https://www.postgresql.org/docs/current/ddl-schemas.html#DDL-SCHEMAS-PATH

.. _PostgreSQL isolation level:
   https://docs.djangoproject.com/en/stable/ref/databases/#isolation-level

.. admonition:: See also

   * :meth:`Env.db() <yaenv.core.Env.db>`
   * :func:`db.parse() <yaenv.db.parse>`
