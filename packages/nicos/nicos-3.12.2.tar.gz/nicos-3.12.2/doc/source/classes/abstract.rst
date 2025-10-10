=======================
Abstract device classes
=======================

These classes are not for direct use as an instrument component, but for
deriving custom device classes from them.  They extend the base classes in
:mod:`nicos.core.device`, which are also abstract, but are a little more
concrete.


.. module:: nicos.devices.abstract

Axis-related classes
--------------------

.. autoclass:: Coder()

.. autoclass:: Motor()

.. autoclass:: Axis()


Mapping device classes
----------------------

.. autoclass:: TransformedReadable()

.. autoclass:: TransformedMoveable()

.. autoclass:: MappedReadable()

.. autoclass:: MappedMoveable()


Special classes
---------------

.. autoclass:: Magnet()
