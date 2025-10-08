Changelog
=========

4.3 (2025-10-07)
----------------

- Ensure connections always reconnect deterministically after a server
  disconnect (or crash).
  Previously the pool may have harboured long-running connections that only
  got reconnected when the pool felt like returning it to the application.
  Those connections can easily have lingered for a long time, causing
  user-visible errors long after the original problem was fixed, e.g. when
  the server has restarted a couple of hours ago.
  (`#7 <https://github.com/dataflake/Products.ZPsycopgDA/pull/7>`_)

- Add support for Python 3.13.

- Drop support for Python 3.7 and 3.8.


4.2 (2023-12-07)
----------------

- Add support for Python 3.12.

- Ensure connection always get properly initialized.

- Add support for PostgreSQL 13.


4.1 (2023-10-04)
----------------

- Add support for reading the connection string from an environment variable.
  Use ``ENV:DB_CONN`` as connection string to look up the actual connection
  string in the environment variable ``DB_CONN``.


4.0 (2023-02-02)
----------------

- Drop support for Python 2.7, 3.5, 3.6.


3.1 (2023-01-16)
----------------

- Update to latest meta/config


3.0 (2023-01-05)
----------------

- Add support for Python 3.11


3.0b1 (2022-08-31)
------------------

- Re-released under the Zope Public License (ZPL) version 2.1

- Updated package layout and name to conform to current Zope standards

- Added compatibility with Zope 4 and Zope 5

- Removed compatibility with Zope 2 and Zope 3

- Added unit and functional tests


2.4.7
-----

- Removed ZPsycopgDA dependencies on deprecated (Python or Zope) features.


2.4.6
-----

- Added all the supported isolation level options
- Fixed pool bugs (psycopg issues #123, #125, #142)


2.4.4
-----

- Make this and egg.
