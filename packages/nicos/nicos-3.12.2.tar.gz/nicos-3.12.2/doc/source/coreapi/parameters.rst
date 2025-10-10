Parameter definition
====================

.. module:: nicos.core.params

The :mod:`nicos.core.params` module defines various helpers that are used when
writing device classes.  They are re-exported in :mod:`nicos.core`.

.. autoclass:: Param(description, type=float, default=_notset, mandatory=False, settable=False, volatile=False, unit=None, category=None, preinit=False, prefercache=None, userparam=True, chatty=False)

.. autoclass:: Override(**keywords)

.. autoclass:: Value

.. autoclass:: Attach

.. autoclass:: ArrayDesc

.. data:: INFO_CATEGORIES

   The categories allowed for `.Device.info()` are:

   * ``'experiment'`` -- Experiment information
   * ``'sample'`` -- Sample and alignment information
   * ``'instrument'`` -- Instrument setup
   * ``'offsets'`` -- Offsets
   * ``'limits'`` -- Limits
   * ``'precisions'`` -- Precisions
   * ``'status'`` -- Instrument status (reserved for `status()` values)
   * ``'general'`` -- Instrument state, i.e. everything else of importance
   * ``'presets'`` -- Detector preset information
   * ``'result'`` -- Updated values after counting


.. _`type-converter-functions`:

Type converter functions
------------------------

These functions can be used as (or used to create) parameter types (i.e. the
*type* argument of `Param` and the *valuetype* attribute of devices) that not
only convert to the correct type (such as `int`, `str` etc.), but also do more
validation of the parameter.


.. function:: anytype

   Converter that accepts anything.  Example::

       Param(..., type=anytype)



The following are converter function factories: when called with some arguments,
they return a converter.

.. function:: intrange(from, to)

   Create a converter that accepts only integers in the ``range(from, to+1)``
   (i.e., *to* is included).  Example::

       Param(..., type=intrange(3, 6), ...)

.. function:: floatrange(from, to)

   Create a converter that accepts only floats between *from* and *to*.
   Example::

       Param(..., type=floatrange(0, 10))

.. function:: nonzero(converter, default=None)

   Creates a converter that restricts the values that the inner *converter*
   allows by disallowing zero.  Examples::

       Param(..., type=nonzero(int, 1))
       Param(..., type=nonzero(floatrange(-10, 10))

   The *default* value is optional except if the *converter* defaults to 0.
   If no *default* value is specified, it is derived from *converter* (if
   nonzero) or the integer 1 (if accepted by *converter*).  If both fail, the
   converter can't be created and raises an error indicating that a *default*
   value needs to be specified, which is both valid for *converter* and nonzero.

.. function:: none_or(converter)

   Create a converter that accepts only ``None`` or what the *converter*
   accepts.  Example::

       Param(..., type=none_or(str))

.. function:: oneof(*values)

   Create a converter that accepts only one of the given *values*.  Example::

       Param(..., type=oneof('up', 'down'))

.. function:: listof(element_converter)

   Create a converter that accepts only lists with element types given by the
   *element_converter*.  Examples::

       Param(..., type=listof(int))
       Param(..., type=listof(anytype))

.. function:: nonemptylistof(element_converter)

   Like `listof`, but the list may not be empty.

.. function:: tupleof(*element_converters)

   Create a converter that accepts only tuples with element types given by the
   *element_converters*.  Examples::

       Param(..., type=tupleof(int, int))
       Param(..., type=tupleof(anytype, str, str))

.. function:: dictof(key_converter, value_converter)

   Create a converter that accepts only dictionaries with key types given by
   *key_converter* and value types given by *value_converter*.  Examples::

       Param(..., type=dictof(str, anytype), ...)
       Param(..., type=dictof(str, int), ...)

.. function:: dictwith(key=value_converter, ...)

   Create a converter that accepts only dictionaries with string keys.  The
   dictionaries must have exactly the keys given to ``dictwith``, and the
   values are converted using the ``value_converter``\s.  For example::

      dictwith(name=str, value=int)

   will accept ``{'name': 'Foo', 'value': 5}`` but not ``{'name': 'Foo'}`` or
   ``{1: 'bar'}``.  ``{'value': 'notanint'}`` will also be rejected.

.. function:: oneofdict(values)

   Create a converter that accepts only the keys and values of the dictionary
   given in *values*.  When one of the keys is given, it is converted to the
   corresponding value.  Example::

       Param(..., type=oneofdict({'up': 1, 'down': 0}))

.. function:: oneofdict_or(named_vals, basic_converter)

   Create a converter that accepts all values the *basic_converter* would also
   accept, plus the strings given as keys in *named_vals*. The mapped values
   must conform to the *basic_converter*.

   Returns only values conforming to the *basic_converter*. Examples::

       Param(..., type=oneofdict_or(dict(refpos=12.34, e=2.718), floatrange(0, 100))

.. function:: setof(values)

   Create a converter that accepts only sequences with the elements given in
   *values*.  Examples::

       Param(..., type=setof(1, 2, 5))
       Param(..., type=setof('guest', 'user', 'admin'))

.. function:: host(defaulthost='', defaultport=None)

   Create a converter that accepts a string in the format ``"host:port"``.
   Default host is empty.  If no default port is given, no port is added
   automatically.  Example::

      Param(..., type=host(defaultport=14869))


The following are simple converters: they are not customizable and can be used
as-is as a parameter type.  Example::

   Param(..., type=vec3, ...)


.. function:: vec3

   Converter that only accepts 3-vectors (i.e. lists or tuples) of floats.

.. function:: limits

   Converter that only accepts a list or tuple of two values, where the second
   value must be greater than the first value.  The first value will be used as
   a lower limit and the second as an upper limit.

.. function:: mailaddress

   Converter that accepts only valid email addresses, but without a check for
   the existence of the mailaddress itself.

.. function:: nonemptystring

   Converter that accepts only a non-empty string.

.. function:: nicosdev

   Converter that only accepts valid NICOS device names.

.. function:: tangodev

   Converter that only accepts valid TANGO device names (must be of the
   form ``tango://host:port/a/b/c``).

.. autofunction:: pvname

   Converter that only accepts valid Epics PV names.

.. autofunction:: ipv4

   Converter that only accepts an IPv4 in string form (``1.2.3.4``).

.. autofunction:: absolute_path

   Converter that only accepts an absolute path.

.. autofunction:: relative_path

   Converter that only accepts a relative path, which also can't go up the
   directory hierarchy using ``../`` or similar.

.. autofunction:: expanded_path

   Converter that takes any path and expands user home (``~``) and environment
   variables (``$var``).

.. autofunction:: subdir

   Converter that only accepts a single subdirectory name, without path
   separators.
