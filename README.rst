====
coid
====

.. image:: https://travis-ci.org/bninja/coid.png
   :target: https://travis-ci.org/bninja/coid

.. image:: https://coveralls.io/repos/bninja/ciao/badge.png
   :target: https://coveralls.io/r/bninja/ciao

Simple resource throttling. Get it:

.. code:: bash

   $ pip install coid

use it e.g. like:

.. code:: python

   import datetime
   
   import ciao
   import sqlalchemy as sa

   db_engine = sa.create_engine('postgres://mikey:corleone@localhost/study')
   
   db_throttle = ciao.Throttle(
     duration=datetime.timedelta(seconds=30),
     exc=(
         sa.exc.OperationalError,
         sa.exc.DisconnectionError,
         sa.exc.InvalidRequestError,
         sa.exc.InterfaceError,
         sa.exc.DatabaseError,
         sa.exc.DBAPIError,
     ),
   )
   
   if not db_throttle:
      with db_throttle:
         db_engine.execute('SELECT * FROM slippers WHERE name = "mine"')
