E-mail
======

Format: ``{scheme}://{user}:{password}@{host}:{port}?{parameters}``

Schemes
-------

* console: ``django.core.mail.backends.console.EmailBackend``
* dummy: ``django.core.mail.backends.dummy.EmailBackend``
* file: ``django.core.mail.backends.filebased.EmailBackend``
* memory: ``django.core.mail.backends.locmem.EmailBackend``
* smtp: ``django.core.mail.backends.smtp.EmailBackend``
* smtp+ssl: ``django.core.mail.backends.smtp.EmailBackend``
* smtp+tls: ``django.core.mail.backends.smtp.EmailBackend``

Parameters
----------

You can define e-mail options as query parameters.

* certfile: EMAIL_SSL_CERTFILE_
* keyfile: EMAIL_SSL_KEYFILE_
* timeout: EMAIL_TIMEOUT_
* localtime: EMAIL_USE_LOCALTIME_

.. _EMAIL_SSL_CERTFILE:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-EMAIL_SSL_CERTFILE

.. _EMAIL_SSL_KEYFILE:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-EMAIL_SSL_KEYFILE

.. _EMAIL_TIMEOUT:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-EMAIL_TIMEOUT

.. _EMAIL_USE_LOCALTIME:
   https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-EMAIL_USE_LOCALTIME

.. admonition:: See also

   * :meth:`Env.email() <yaenv.core.Env.email>`
   * :func:`email.parse() <yaenv.email.parse>`
