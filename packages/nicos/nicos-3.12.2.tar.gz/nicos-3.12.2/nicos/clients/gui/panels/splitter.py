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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Support for "auxiliary" windows containing panels."""

from nicos.clients.gui.panels.base import SetupDepPanelMixin
from nicos.guisupport.qt import QSplitter, Qt
from nicos.utils.loggers import NicosLogger


class Splitter(QSplitter, SetupDepPanelMixin):
    setWidgetVisible = SetupDepPanelMixin.setWidgetVisible

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        from nicos.clients.gui.panels.utils import createWindowItem
        QSplitter.__init__(self, parent)
        window.splitters.append(self)
        self.log = NicosLogger('Splitter')
        self.log.parent = topwindow.log
        SetupDepPanelMixin.__init__(self, window.client, item.options)
        for subitem in item.children:
            sub = createWindowItem(subitem, window, menuwindow, topwindow,
                                   self.log)
            if sub:
                self.addWidget(sub)


class VerticalSplitter(Splitter):

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        Splitter.__init__(self, item, window, menuwindow, topwindow, parent)
        self.setOrientation(Qt.Orientation.Vertical)


class HorizontalSplitter(Splitter):

    def __init__(self, item, window, menuwindow, topwindow, parent=None):
        Splitter.__init__(self, item, window, menuwindow, topwindow, parent)
        self.setOrientation(Qt.Orientation.Horizontal)
