# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""
Base class for NICOS UI widgets.
"""

from copy import copy

from nicos.core.constants import NOT_AVAILABLE
from nicos.core.status import OK
from nicos.guisupport.qt import QFont, QFontMetrics, pyqtProperty
from nicos.protocols.daemon import DAEMON_EVENTS
from nicos.utils import KEYEXPR_NS, AttrDict, lazy_property, parseKeyExpression


class NicosListener:
    """Base mixin class for an object that can receive cache events."""

    def setSource(self, source):
        self._source = source
        self._devmap = {}
        self.devinfo = {}
        self.registerKeys()

    def _newDevinfo(self, expr, unit, fmtstr, isdevice):
        return AttrDict(
            {'value': '-',
             'expr': expr,
             'strvalue': '-',
             'fullvalue': '-',
             'status': (OK, ''),
             'fmtstr': fmtstr or '%s',
             'unit': unit,
             'fixed': '',
             'changetime': 0,
             'expired': True,
             'isdevice': isdevice})

    def registerDevice(self, dev, unit='', fmtstr=''):
        if not dev:
            return
        key, expr, _ = parseKeyExpression(
            dev, append_value=False, normalize=lambda s: s.lower())
        self.devinfo[key] = self._newDevinfo(expr, unit, fmtstr, True)
        self._devmap[self._source.register(self, key + '/value')] = key
        self._devmap[self._source.register(self, key + '/status')] = key
        self._devmap[self._source.register(self, key + '/fixed')] = key
        if not unit:
            self._devmap[self._source.register(self, key + '/unit')] = key
        if not fmtstr:
            self._devmap[self._source.register(self, key + '/fmtstr')] = key

    def registerKey(self, valuekey, statuskey='', unit='', fmtstr=''):
        if not valuekey:
            return
        key, expr, _ = parseKeyExpression(valuekey, append_value=False)
        self.devinfo[key] = self._newDevinfo(expr, unit, fmtstr, False)
        self._devmap[self._source.register(self, key)] = key
        if statuskey:
            self._devmap[self._source.register(self, statuskey)] = key

    def registerKeys(self):
        """Register any keys that should be watched."""
        raise NotImplementedError('Implement registerKeys() in %s' %
                                  self.__class__)

    def on_keyChange(self, key, value, time, expired):
        """Default handler for changing keys.

        The default handler handles changes to registered devices.
        """
        if key not in self._devmap:
            return
        devinfo = self.devinfo[self._devmap[key]]
        if devinfo.isdevice:
            if key.endswith('/status'):
                if value is None:
                    value = devinfo.status
                    expired = True
                devinfo.status = value
                devinfo.changetime = time
                self.on_devStatusChange(self._devmap[key],
                                        value[0], value[1], expired)
                return
            elif key.endswith('/fixed'):
                if value is None:
                    return
                devinfo.fixed = value
                self.on_devMetaChange(self._devmap[key], devinfo.fmtstr,
                                      devinfo.unit, devinfo.fixed)
                return
            elif key.endswith('/fmtstr'):
                if value is None:
                    return
                devinfo.fmtstr = value
                self._update_value(key, devinfo, devinfo.value,
                                   devinfo.expired)
                self.on_devMetaChange(self._devmap[key], devinfo.fmtstr,
                                      devinfo.unit, devinfo.fixed)
                return
            elif key.endswith('/unit'):
                if value is None:
                    return
                devinfo.unit = value
                self.on_devMetaChange(self._devmap[key], devinfo.fmtstr,
                                      devinfo.unit, devinfo.fixed)
                return
        # it's either /value, or any key registered as value
        # first, apply item selection
        if value is not None:
            if devinfo.expr:
                try:
                    fvalue = eval(devinfo.expr, KEYEXPR_NS, {'x': value})
                except Exception:
                    fvalue = NOT_AVAILABLE
            else:
                fvalue = value
        else:
            fvalue = value
        devinfo.value = fvalue
        devinfo.changetime = time
        self._update_value(key, devinfo, fvalue, expired)

    def _update_value(self, key, devinfo, fvalue, expired):
        if fvalue is None:
            strvalue = '----'
        else:
            if isinstance(fvalue, list):
                fvalue = tuple(fvalue)
            try:
                strvalue = devinfo.fmtstr % fvalue
            except Exception:
                strvalue = str(fvalue)
        devinfo.fullvalue = (strvalue + ' ' + (devinfo.unit or '')).strip()
        if devinfo.strvalue != strvalue or devinfo.expired != expired:
            devinfo.strvalue = strvalue
            devinfo.expired = expired
            self.on_devValueChange(self._devmap[key], fvalue, strvalue,
                                   devinfo.fullvalue, expired)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        pass

    def on_devStatusChange(self, dev, code, status, expired):
        pass

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        pass


class PropDef(pyqtProperty):
    all_types = [
        str, float, int,
        'bool',  # only works as C++ type name
    ]

    def __init__(self, prop, ptype, default, doc=''):
        if ptype is bool:
            ptype = 'bool'
        if ptype not in self.all_types:
            if not (isinstance(ptype, str) and ptype.startswith('Q')):
                raise Exception('invalid property type: %r' % ptype)
        self.ptype = ptype
        self.default = default
        self.doc = doc

        def getter(self):
            return self.props[prop]

        def setter(self, value):
            value = PropDef.convert(value)
            self.props[prop] = value
            self.propertyUpdated(prop, value)

        def resetter(self):
            if callable(default):
                setattr(self, prop, default(self))
            else:
                setattr(self, prop, default)

        pyqtProperty.__init__(self, ptype, getter, setter, resetter, doc=doc)

    @staticmethod
    def convert(value):
        if isinstance(value, QFont):
            # QFont doesn't like to be copied with copy()...
            return QFont(value)
        return copy(value)


class NicosWidget(NicosListener):
    """Base mixin class for a widget that can receive cache events.

    This class can't inherit directly from QObject because Python classes
    can only derive from one PyQt base class, and that base class will be
    different for different widgets.
    """

    # source for cache keys
    _source = None
    # daemon-client object, only present when used in the GUI client
    _client = None

    # set this to a description of the widget for the Qt designer
    designer_description = ''
    # set this to an icon name for the Qt designer
    designer_icon = None

    # define properties
    valueFont = PropDef('valueFont', 'QFont', QFont('Monospace'),
                        'Font used for displaying values')

    # collects all properties of self's class
    @lazy_property
    def properties(self):
        props = {}
        for attrname in dir(self.__class__):
            attr = getattr(self.__class__, attrname)
            if isinstance(attr, pyqtProperty):
                props[attrname] = attr
        return props

    # dictionary for storing current property values
    @lazy_property
    def props(self):
        return {}

    def __init__(self):
        for prop, pdef in self.properties.items():
            if prop not in self.props:
                if callable(pdef.default):
                    self.props[prop] = PropDef.convert(pdef.default(self))
                else:
                    self.props[prop] = PropDef.convert(pdef.default)
        self._scale = QFontMetrics(self.valueFont).horizontalAdvance('0')
        self.initUi()

    def initUi(self):
        """Create user interface if necessary."""

    def propertyUpdated(self, pname, value):
        """Called when a property in self.properties has been updated."""
        if pname == 'valueFont':
            self._scale = QFontMetrics(value).horizontalAdvance('0')
        self.update()

    def setClient(self, client):
        self.setSource(client)
        self._client = client
        # refresh all keys at widget creation time to get an initial value
        for key in self._devmap:
            ret = self._client.getCacheKey(key)
            if ret:
                self.on_keyChange(ret[0], ret[1], 0, False)
        # auto-connect client signal handlers
        for signal in DAEMON_EVENTS:
            handler = getattr(self, 'on_client_' + signal, None)
            if handler:
                getattr(self._client, signal).connect(handler)
