.. _json-head:

JSON Configuration Format
=========================

This page describes the JSON configuration format for HERO devices.
The JSON configuration can be provided as a single HERO config object or as a collection of HERO configs under the ``rows`` key.

Single HERO Config
~~~~~~~~~~~~~~~~~~

A single HERO config is a dictionary with the following keys:

.. code-block:: json

   {
       "_id": "hero_name",
       "classname": "module.class",
       "arguments": {},
       "datasource": {}
   }

.. list-table::
   :widths: 15 10 30
   :header-rows: 1

   * - Key
     - Type
     - Description
   * - ``_id``
     - string
     - Name of the HERO.
   * - ``classname``
     - string
     - Path to the device driver class in the form ``module.class``.
   * - ``arguments``
     - dict
     - Dictionary of keyword-value pairs passed to the ``__init__`` function of the class specified in ``classname``.
   * - ``datasource`` (optional)
     - dict
     - Keyword-value pairs that describe a datasource (classes with the ``observable_data`` function).
   * - ``tags`` (optional)
     - list
     - List of tags that are added to the HERO. The tag ``BOSS: {name_of_boss}`` is always added to the tag list independent of this configuration.

Special Arguments
~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "_id": "hero_name_1",
        "classname": "module.class",
        "arguments": {
            "loop": "@_boss_loop",
            "pool": "@_boss_pool"
        }
    }

Event Loop
^^^^^^^^^^
Using ``@_boss_loop`` as the value of the key/value pair in the ``arguments`` part of the configuration passes the ``asyncio.EventLoop`` which is running inside ``BOSS``.
Note, ``asyncio`` support in Zenoh is still in development and using the event loop might not behave as expected.

Process Pool
^^^^^^^^^^^^
Upon start, ``BOSS`` creates an ``concurrent.futures.ProcessPoolExecutor``, this pool can be passed to the target class via ``@_boss_pool``.
The number of workers can be controlled via the parameter ``--max-workers`` when starting ``BOSS``.

Datasource Keys
~~~~~~~~~~~~~~~

The ``datasource`` dictionary supports the following keys:

.. list-table::
   :widths: 15 10 30
   :header-rows: 1

   * - Key
     - Type
     - Description
   * - ``async``
     - bool
     - If ``true``, the device class handles the ``observable_data`` event by itself. If ``false``, the ``observable_data`` function is polled periodically.
   * - ``interval``
     - number
     - Polling interval in seconds.
   * - ``observable``
     - list
     - List of class attributes that are polled and emitted with the ``observable_data`` event.

Multiple HERO Configs
~~~~~~~~~~~~~~~~~~~~~

To define multiple HERO configs, use the ``rows`` key:

.. code-block:: json

   {
       "rows": [
           {
               "_id": "hero_name_1",
               "classname": "module.class",
               "arguments": {},
               "datasource": {}
           },
           {
               "_id": "hero_name_2",
               "classname": "module.class",
               "arguments": {},
               "datasource": {}
           }
       ]
   }


.. warning::

  The ``couchdb`` API may enclose the HERO config dictionary in a ``doc`` keyword. This is handled automatically, so **do not** use ``doc`` as a top-level key in your configuration.


.. tip::

  You may use additional keys for specific use cases, such as CouchDB views. For more information, see :ref:`couchdb-view`.


