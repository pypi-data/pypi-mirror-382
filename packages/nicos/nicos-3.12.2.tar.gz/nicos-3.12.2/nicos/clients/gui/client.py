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

"""NICOS daemon client object for the GUI."""

from time import time as currenttime
from weakref import ref

from nicos.clients.base import NicosClient
from nicos.guisupport.qt import QObject, pyqtSignal
from nicos.protocols.cache import OP_TELLOLD, cache_load
from nicos.protocols.daemon import DAEMON_EVENTS
from nicos.utils.loggers import NicosLogger


class NicosGuiClient(NicosClient, QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    broken = pyqtSignal(object)
    failed = pyqtSignal(object, object)
    error = pyqtSignal(object)
    initstatus = pyqtSignal(object)

    for evk, event in DAEMON_EVENTS.items():
        if event[1]:
            locals()[evk] = pyqtSignal(object, object)
        else:
            locals()[evk] = pyqtSignal(object)

    def __init__(self, parent, parent_logger):
        QObject.__init__(self, parent)
        logger = NicosLogger('client')
        logger.parent = parent_logger
        NicosClient.__init__(self, logger.warning)
        self._reg_keys = {}
        self._event_mask = ['livedata']
        self.cache.connect(self.on_cache_event)
        self.connected.connect(self.on_connected_event)

    def signal(self, name, *args):
        getattr(self, name).emit(*args)

    def connect(self, conndata, eventmask=None):
        NicosClient.connect(self, conndata, self._event_mask)

    # key-notify registry

    def register(self, widget, key):
        """API used by NicosListener widgets to register keys for callback."""
        key = key.lower()
        # use weakrefs so that we don't keep the widgets alive
        self._reg_keys.setdefault(key, []).append(ref(widget))
        return key

    def on_cache_event(self, data):
        (time, key, op, value) = data
        if key in self._reg_keys:
            try:
                cvalue = cache_load(value)
            except ValueError:
                cvalue = None
            for widget in self._reg_keys[key]:
                if widget():
                    widget().on_keyChange(key, cvalue, time,
                                          not value or op == OP_TELLOLD)

    def on_connected_event(self):
        # request initial value for all keys we have registered
        if not self._reg_keys:
            return
        values = self.ask('getcachekeys', ','.join(self._reg_keys), quiet=True,
                          default=[])
        for key, value in values:
            # Not all keys are registered!
            for widget in self._reg_keys.get(key, ()):
                if widget():
                    widget().on_keyChange(key, value, currenttime(), False)
