Module LogP
===========
Set up a logging-environment for daemons or console-programs

Copyright (c) 2022 Ing. Rainer Pietsch <r.pietsch@pcs-at.com>

Detailed docs at <https://pcs-log.readthedocs.io/en/latest/index.html>

Source at <https://github.com/rpietsch1953/Log>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

Usage:
------

.. code-block:: python

    import logging
    from pcs_log.LogP import LogP

.. note::

    you have to import this both in all your modules you like to
    use this logging. But you only need to SetupLogging once.
