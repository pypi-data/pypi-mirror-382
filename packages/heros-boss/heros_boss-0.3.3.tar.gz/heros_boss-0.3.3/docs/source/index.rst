BOSS: Configuration driven object/HERO starter
==============================================

BOSS is a service that instanciates python objects as HEROs based on a JSON configuration. The configuration
can be read from a file, a URL (e.g. from a :ref:`CouchDB <couchdb-head>`) or from an environment variable. Basically, BOSS allows
you to quickly mask your arbitrary python object as a HERO and to run it.

The configuration sources (for example an URL specified by the :code:`-u` command line argument)
can be reloaded in-situ without disturbing the running HEROs by using :py:meth:`boss.boss.BOSS.refresh_hero_sources`.
Sources can also be added and removed by using :py:meth:`boss.boss.BOSS.add_hero_source` or by manipulating the
:py:attr:`boss.boss.BOSS.sources` list directly.

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   couchdb
   json
   autoapi/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
