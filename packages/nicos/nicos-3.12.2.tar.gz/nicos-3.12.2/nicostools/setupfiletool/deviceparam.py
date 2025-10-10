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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************
"""Classes to handle the device parameters."""

from os import path

from nicos.guisupport.qt import QWidget, pyqtSignal, uic


class DeviceParam(QWidget):
    editedParam = pyqtSignal()
    clickedRemoveButton = pyqtSignal(str)

    def __init__(self, param, valueWidget, isUnknownValue=False, parent=None):
        QWidget.__init__(self, parent)
        uic.loadUi(path.abspath(path.join(path.dirname(__file__),
                                          'ui',
                                          'deviceparam.ui')), self)
        self.placeholder.setVisible(False)
        self.param = param
        self.valueWidget = valueWidget
        self.isUnknownValue = isUnknownValue
        self.pushButtonRemove.clicked.connect(
            lambda: self.clickedRemoveButton.emit(self.param))
        self.labelParam.setText(self.param + ':')
        self.horizontalLayout.addWidget(self.valueWidget)
        self.valueWidget.valueModified.connect(self.editedParam)
        self.valueWidget.valueChosen.connect(lambda _: self.editedParam.emit())

    def getValue(self):
        return self.valueWidget.getValue()
