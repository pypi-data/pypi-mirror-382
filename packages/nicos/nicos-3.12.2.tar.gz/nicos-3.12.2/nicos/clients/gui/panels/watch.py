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

"""NICOS GUI watch variable panel component."""

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QInputDialog, QMessageBox, QTreeWidgetItem, \
    pyqtSlot
from nicos.guisupport.utils import setBackgroundColor


class WatchPanel(Panel):
    """Provides a way to enter "watch expressions".

    It works similar to a debugger and evaluates the expressions regularly.
    """

    panelName = 'Watch'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/watch.ui')

        self.watch_items = {}
        client.watch.connect(self.on_client_watch)
        client.initstatus.connect(self.on_client_initstatus)

    def setCustomStyle(self, font, back):
        self.watchView.setFont(font)
        setBackgroundColor(self.watchView, back)

    def updateStatus(self, status, exception=False):
        isconnected = status != 'disconnected'
        self.addWatch.setEnabled(isconnected)
        self.deleteWatch.setEnabled(isconnected)
        self.oneShotEval.setEnabled(isconnected)

    def on_client_initstatus(self, state):
        self.on_client_watch(state['watch'])

    def on_client_watch(self, data):
        values = data
        names = set()
        for name, val in values.items():
            name = name[:name.find(':')]
            if name in self.watch_items:
                self.watch_items[name].setText(1, str(val))
            else:
                newitem = QTreeWidgetItem(self.watchView,
                                          [str(name), str(val)])
                self.watchView.addTopLevelItem(newitem)
                self.watch_items[name] = newitem
            names.add(name)
        removed = set(self.watch_items) - names
        for itemname in removed:
            self.watchView.takeTopLevelItem(
                self.watchView.indexOfTopLevelItem(
                    self.watch_items[itemname]))
            del self.watch_items[itemname]

    @pyqtSlot()
    def on_addWatch_clicked(self):
        expr, ok = QInputDialog.getText(self, 'Add watch expression',
                                        'New expression to watch:')
        if not ok:
            return
        newexpr = [expr + ':default']
        self.client.tell('watch', newexpr)

    @pyqtSlot()
    def on_deleteWatch_clicked(self):
        item = self.watchView.currentItem()
        if not item:
            return
        expr = item.text(0)
        delexpr = [expr + ':default']
        self.client.tell('unwatch', delexpr)

    @pyqtSlot()
    def on_oneShotEval_clicked(self):
        expr, ok = QInputDialog.getText(self, 'Evaluate an expression',
                                        'Expression to evaluate:')
        if not ok:
            return
        ret = self.client.eval(expr, stringify=True)
        QMessageBox.information(self, 'Result', ret)
