Usage
=====

.. _installation:

Installation
------------

To use pcs_log, first install it using pip:

.. code-block:: console

   (.venv) $ pip install pcs_log

Use in your program
-------------------

This module handles the most often used logging options:
 - log to console
 - log to syslog
 - log to file with autorotation
 - additional a standalone logging server accessible via telnet
 - multiprocessing logs
 - mutithreading logs
 - enhanced formatting options


normally imported as


.. code-block:: python

    from pcs_alog.Logp import LogP


Check out :doc:`examples`

