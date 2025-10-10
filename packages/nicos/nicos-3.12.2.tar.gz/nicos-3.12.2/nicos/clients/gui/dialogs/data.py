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

"""Dialog for exporting data."""

from nicos.guisupport.qt import QComboBox, QFileDialog, QLabel


class DataExportDialog(QFileDialog):

    def __init__(self, viewplot, curvenames, *args):
        QFileDialog.__init__(self, viewplot, *args)
        self.setOption(self.Option.DontConfirmOverwrite, False)
        # allow adding some own widgets
        self.setOption(self.Option.DontUseNativeDialog, True)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        layout = self.layout()
        layout.addWidget(QLabel('Curve:', self), 4, 0)
        self.curveCombo = QComboBox(self)
        if len(curvenames) > 1:
            self.curveCombo.addItem('all (in separate files)')
            self.curveCombo.addItem('all (in one file, multiple data columns)')
        self.curveCombo.addItems(curvenames)
        layout.addWidget(self.curveCombo, 4, 1)
        layout.addWidget(QLabel('Time format:', self), 5, 0)
        self.formatCombo = QComboBox(self)
        self.formatCombo.addItems(['Seconds since first datapoint',
                                   'UNIX timestamp',
                                   'Text timestamp (YYYY-MM-dd.HH:MM:SS)'])
        layout.addWidget(self.formatCombo, 5, 1)
