.. _couchdb-head:

CouchDB for BOSS
################

`CouchDB <https://couchdb.apache.org/>`_ is a document based database, which can provide JSON strings for BOSS devices.

To get started, install an instance of CouchDB, for example in a `docker container <https://docs.couchdb.org/en/stable/install/docker.html>`_.

After creating a database (in this example, we created a database `my-boss`) as described in the official CouchDB documentation,
we can now create a CouchDB document with the following content:

.. code-block:: json

  {
    "_id": "http-test",
    "classname": "http.client.HTTPConnection",
    "arguments": {
      "host": "gitlab.com"
    }
  }

.. hint::

   It is also possible to include multiple devices in a single document like:

   .. code-block:: json

        {
          "_id": "multi-devices",
          "rows": [
            { "<device definition>" },
            { "<device definition>" },
          ]
        }


This example launches a simple HTTP Connection to gitlab. You can simply use a different class in the :code:`classname` entry to
use your device driver or any other arbitrary class you want to expose as HERO.


To use BOSS to start the HERO defined above, run

.. code-block:: bash

   python -m boss.starter -u http://<user>:<pw>@<couchdb_host>:5984/my-boss/http-test


If you want to run all documents/devices in the database you can run

.. note::

   This is not recommended in production. Use a view (see below) instead to avoid loading invalid documents and the ability to
   switch off/on devices quickly.


.. code-block:: bash

   python -m boss.starter -u http://<user>:<pw>@<couchdb_host>:5984/my-boss/_all_docs?include_docs=true


.. _couchdb-view:

Using Views
-----------

To make a view which includes all active devices, add a `Design Document` view entry with the following map function:

.. code-block::

   function(doc) {
    if(doc.active) {
      emit()
    }
   }

With the following boss command, you can than start all devices that have the key :code:`active` set to :code:`true` in their json definition:

.. code-block:: bash

   python -m boss.starter -u http://<user>:<pw>@<couchdb_host>:5984/my-boss/_design/active/_view/active?include_docs=true


.. hint::

   If you want to directly see if your settings worked, you can use our rudimentary `GUI <https://gitlab.com/atomiq-project/hero-monitor>`_.
