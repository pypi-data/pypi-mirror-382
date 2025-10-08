Installation
============


Prerequisites
-------------
You need to have PostGreSQL libraries and developer files installed prior to
installing :mod:`Products.ZPsycopgDA`.


Install with ``pip``
--------------------

.. code:: 

    $ pip install Products.ZPsycopgDA


Install with ``zc.buildout``
----------------------------
Just add :mod:`Products.ZPsycopgDA` to the ``eggs`` setting(s) in your
buildout configuration to have it pulled in automatically::

    ...
    eggs =
        Products.ZPsycopgDA
    ...
