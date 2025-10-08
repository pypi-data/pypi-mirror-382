Development
===========

Bug tracker
-----------
For bug reports, suggestions or questions please use the 
GitHub issue tracker at
https://github.com/dataflake/Products.ZPsycopgDA/issues.


Getting the source code
-----------------------
The source code is maintained on GitHub. To check out the main branch:

.. code-block:: console

  $ git clone https://github.com/dataflake/Products.ZPsycopgDA.git

You can also browse the code online at
https://github.com/dataflake/Products.ZPsycopgDA


Preparing the development sandbox
---------------------------------
The following steps only need to be done once to install all the tools and
scripts needed for building, packaging and testing. First, create a
:term:`Virtual environment`. The example here uses Python 3.11, but any Python
version supported by this package will work. Then install all the required
tools:

.. code-block:: console

    $ cd Products.ZPsycopgDA
    $ python3.11 -m venv .
    $ bin/pip install -U pip wheel
    $ bin/pip install -U setuptools zc.buildout tox twine


Running the tests
-----------------
You can use ``tox`` to run the unit and integration tests in this package. The
shipped ``tox`` configuration can run the tests for all supported platforms.
You can read the entire long list of possible options on the
`tox CLI interface documentation page
<https://tox.wiki/en/latest/cli_interface.html>`_, but the following examples
will get you started:

.. code-block:: console

    $ bin/tox -l       # List all available environments
    $ bin/tox -pall    # Run tests for all environments in parallel
    $ bin/tox -epy311  # Run tests on Python 3.11 only
    $ bin/tox -elint   # Run package sanity checks and lint the code


Running the functional tests
----------------------------
Some tests are hard or even impossible to perform without a real running
database backend. During a normal test run they will be skipped, and
you will see output like this::

  Total: 62 tests, 0 failures, 0 errors and 5 skipped in 0.090 seconds.

To run those functional tests you need to have a PostgreSQL server
running and listening on the standard unix socket, normally
located at ``/var/run/postgresql/.s.PGSQL.5432``. This database server must
have a database named ``zpsycopgdatest`` that can be accessed by a user
``zpsycopgdatest`` with password ``zpsycopgdatest``. To set this up, log into
the running database server with an admin user and execute the following
statements::

  postgres=# CREATE USER zpsycopgdatest WITH PASSWORD 'zpsycopgdatest';
  postgres=# CREATE DATABASE zpsycopgdatest;

If everything worked you'll see test output like this::

  Total: 62 tests, 0 failures, 0 errors and 0 skipped in 0.105 seconds.


Building the documentation
--------------------------
``tox`` is also used to build the :term:`Sphinx`-based documentation. The
input files are in the `docs` subfolder and the documentation build step will
compile them to HTML. The output is stored in `docs/_build/html/`:

.. code-block:: console

    $ bin/tox -edocs

If the documentation contains doctests they are run as well.
