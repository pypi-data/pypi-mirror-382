.. image:: https://img.shields.io/pypi/v/pexy.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/pexy/
.. image:: https://github.com/clivern/pexy/actions/workflows/ci.yml/badge.svg
    :alt: Build Status
    :target: https://github.com/clivern/pexy/actions/workflows/ci.yml

|

=====
Pexy
=====

To use pexy, follow the following steps:

1. Create a python virtual environment or use system wide environment

.. code-block::

    $ python3 -m venv venv
    $ source venv/bin/activate


2. Install pexy package with pip.

.. code-block::

    $ pip install pexy


3. Get pexy command line help

.. code-block::

    $ pexy --help


4. Get pexy version

.. code-block::

    $ pexy --version


5. Get Store Info

.. code-block::

    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx store info


6. Get Access Scope.

.. code-block::

    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx access scope


7. Collection commands.

.. code-block::

    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx collection create -p payload.json
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx collection update <id> -p payload.json
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx collection list <id>,<id>
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx collection get <id>
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx collection count
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx collection delete <id>


8. Product commands.

.. code-block::

    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product list
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product list <id>,<id>
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product get <id>
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product count
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product delete <id>
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product create -p payload.json
    $ pexy --name xxxxx-xx --token shpat_xxxxxxxxxxxxx product update <id> -p payload.json
