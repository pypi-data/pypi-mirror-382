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

"""Tree widget for displaying devices/params.
"""

from nicos.guisupport.qt import QTreeWidget, QTreeWidgetItem
from nicos.guisupport.widget import NicosWidget, PropDef


class BaseDeviceParamTree(QTreeWidget):

    def __init__(self, parent, designMode=False, **kwds):
        QTreeWidget.__init__(self, parent, **kwds)
        self._showparams = True
        self.only_explicit = True
        self.device_clause = None
        self.param_predicate = lambda name, value, info: True
        self.item_callback = lambda item, parent=None: True
        self.itemExpanded.connect(self.on_itemExpanded)

    def setClient(self, client):
        self.client = client
        self._reinit()

    def on_client_connected(self):
        self._reinit()

    def on_client_device(self, data):
        self._reinit()

    def registerKeys(self):
        pass

    def on_itemExpanded(self, item):
        if item.childCount():
            return
        devname = item.text(0)
        if self._showparams:
            paraminfo = self.client.getDeviceParamInfo(devname)
            for param, value in sorted(
                    self.client.getDeviceParams(devname).items()):
                if not self.param_predicate(param, value,
                                            paraminfo.get(param)):
                    continue
                subitem = QTreeWidgetItem([param])
                if not self.item_callback(subitem, item):
                    continue
                item.addChild(subitem)

    def _reinit(self):
        self.clear()
        for devname in self.client.getDeviceList(
                only_explicit=self.only_explicit,
                special_clause=self.device_clause):
            item = QTreeWidgetItem([devname])
            # allow expanding interactively, even if we haven't populated
            # the parameter children yet
            item.setChildIndicatorPolicy(
                QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            if not self.item_callback(item):
                continue
            self.addTopLevelItem(item)


class DeviceParamTree(NicosWidget, BaseDeviceParamTree):

    designer_description = 'Displays devices and their parameters'

    showparams = PropDef('showparams', bool, True, 'Show parameters as subitems')

    def __init__(self, parent, designMode=False, **kwds):
        BaseDeviceParamTree.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)

    def setClient(self, client):
        NicosWidget.setClient(self, client)
        BaseDeviceParamTree.setClient(self, client)

    def propertyUpdated(self, pname, value):
        if pname == 'showparams':
            self._showparams = value
        NicosWidget.propertyUpdated(self, pname, value)
