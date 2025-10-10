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
#   Pascal Neubert <pascal.neubert@frm2.tum.de>
#
# *****************************************************************************

from os import path

from nicos.guisupport.qt import QMainWindow, QWidgetItem, uic


class WatcherWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)), 'ui',
                             'watcher.ui'), self)
        self.buttonClear.clicked.connect(self.clear)

    def addWidgetKey(self, widget):
        """Insert the given widget into the watcher window."""
        layout = self.scrollContents.layout()
        layout.insertWidget(layout.count() - 1, widget)

    def clear(self):
        """Remove all watched items."""
        layout = self.scrollContents.layout()
        for i in range(layout.count()-1, -1, -1):
            item = layout.takeAt(i)
            if isinstance(item, QWidgetItem):
                item.widget().deleteLater()
        layout.addStretch()
