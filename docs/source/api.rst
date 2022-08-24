LogP reference
===============

.. note::

   Normally you import only "LogP" from this module.

   .. code-block:: python

      import logging
      from pcs_log.LogP import LogP

   This is a "singleton" and used for all your code-modules. You should insert this two lines 
   in every module using logging, but call :func:`SetupLogging` only once. (except you make your program
   or parts of it to "daemons", in this case you MUST call this function **AFTER** daemonizing within the
   daemonized codeblock again, because all the file-handles are deleted on daemonizing)

.. autoclass:: LogP._LogP
   :members:
