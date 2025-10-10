CAErp asynchronous tasks
============================

Since version 6, caerp-celery only supports python 3.

Asynchronous tasks are executed through celery.
pyramid_celery is used to integrate celery with the Pyramid related stuff.
pyramid_beaker is used to cache responses.

tasks:

    Asynchronous tasks called from CAErp

scheduler:

    Beat tasks, repeated along the time (like cron tasks)

Results
-------

No result backend is used, tasks interact directly with CAErp's database to
return datas.

CAErp celery provides all the models that should be used to store task
execution related stuff (see caerp_celery.models).

Install
-------

System packages
................

autonmie_celery needs a redis server to run

On Debian

.. code-block:: console

    apt-get install redis-server


On Fedora

.. code-block:: console

    dnf install redis-server

Python stuff
.............

caerp_celery should be run in the same environment as CAErp :
https://framagit.org/caerp/caerp

You may first run

.. code-block:: console

    workon caerp


.. code-block:: console

    git clone https://framagit.org/caerp/caerp_celery.git
    cd caerp_celery
    python setup.py install
    cp development.ini.sample development.ini

Customize the development.ini file as needed


Start it
---------

Launch the following command to launch the worker daemon::

    celery -A pyramid_celery.celery_app worker --ini development.ini

Launch the following command to launch the beat daemon::

    celery -A pyramid_celery.celery_app beat --ini development.ini


Customize accounting operation parser and producer for different general_ledger files
---------------------------------------------------------------------------------------

In the inifile of your celery service, configure service factories

Sage (default)
...............

.. code-block::

    caerp_celery.interfaces.IAccountingFileParser=caerp_celery.parsers.sage.parser_factory

.. code-block::

    caerp_celery.interfaces.IAccountingOperationProducer=caerp_celery.parsers.sage.producer_factory

Sage Generation Expert
.......................

.. code-block::

    caerp_celery.interfaces.IAccountingFileParser=caerp_celery.parsers.sage_generation_expert.parser_factory

.. code-block::

    caerp_celery.interfaces.IAccountingOperationProducer=caerp_celery.parsers.sage_generation_expert.producer_factory

Quadra
.......................

.. code-block::

    caerp_celery.interfaces.IAccountingFileParser=caerp_celery.parsers.quadra.parser_factory

.. code-block::

    caerp_celery.interfaces.IAccountingOperationProducer=caerp_celery.parsers.quadra.producer_factory
