.. index:: !history, !history-plotter, !nicos-history
.. _history:

The NICOS history plotter
=========================

This application is a standalone version of the "history" panel that can be used
from the GUI: it displays values from the cache over time.  It is useful if no
daemon is running.


Invocation
----------

The history plotter is invoked with the ``nicos-history`` script::

   nicos-history [options] [view ...]

It has a few options:

.. program:: history

.. option:: -h, --help

    show the help message and exit
.. option:: -c server, --cache server

    connect to the cache at this location ("host[:port]", the default is
    localhost)

.. option:: -p prefix, --prefix prefix

    set prefix of the cache keys, normally you don't have to set this

Also, you can give "view" arguments on the command line to open plots at
startup.  For example::

   nicos-history T_cryo,T_cryo.setpoint

A time specification can be given with a colon::

   nicos-history T_cryo,T_cryo.setpoint:24h

A separate view plot is opened for each such argument.
