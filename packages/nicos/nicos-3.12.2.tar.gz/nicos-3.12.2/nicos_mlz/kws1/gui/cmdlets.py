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

"""Commandlets for KWS(-1)."""

from nicos.clients.gui.cmdlets import Cmdlet, register
from nicos.guisupport.qt import QDialog, QIcon, QMessageBox, QSize, \
    QTableWidgetItem, QToolButton, pyqtSlot
from nicos.utils import findResource, formatDuration

from nicos_mlz.kws1.gui.measdialogs import LOOPS, DetsetDialog, \
    DevicesDialog, MeasDef, RtConfigDialog, SampleDialog


class MeasureTable(Cmdlet):

    name = 'Measurement'
    category = 'Measure'

    meas_def_class = MeasDef

    def __init__(self, parent, client, options):
        uipath = findResource('nicos_mlz/kws1/gui/table.ui')
        Cmdlet.__init__(self, parent, client, options, uipath)
        self.measdef = self.meas_def_class(rtmode=False)
        self.rt_settings = RtConfigDialog.DEFAULT_SETTINGS.copy()
        self.rtConfBtn.setEnabled(False)
        self.updateTable()
        for loop in LOOPS:
            self.outerLoop.addItem(loop)
        self.outerLoop.setCurrentIndex(0)
        client.experiment.connect(self.on_client_experiment)
        self.expandBtn = QToolButton()
        self.expandBtn.setIcon(QIcon(':/down'))
        self.expandBtn.setAutoRaise(True)
        self.expandBtn.clicked.connect(self.on_expandBtn_clicked)
        self.table.setCornerWidget(self.expandBtn)

    @pyqtSlot()
    def on_expandBtn_clicked(self):
        self.table.setMinimumSize(QSize(0, self.table.height() + 100))

    @pyqtSlot()
    def on_selSamples_clicked(self):
        if not self.client.isconnected:
            QMessageBox.warning(self, 'Error', 'You must be connected to '
                                'a daemon to be able to select samples.')
            return
        dlg = SampleDialog(self, self.measdef, self.client)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.measdef.samplefile = dlg.samplefile
        self.measdef.samples = dlg.toDefs()
        self.updateTable()

    @pyqtSlot()
    def on_selDetsets_clicked(self):
        if not self.client.isconnected:
            QMessageBox.warning(self, 'Error', 'You must be connected to '
                                'a daemon to be able to select settings.')
            return
        dlg = DetsetDialog(self, self.measdef, self.client)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.measdef.detsets = dlg.toDefs()
        self.updateTable()

    @pyqtSlot()
    def on_selDevices_clicked(self):
        if not self.client.isconnected:
            QMessageBox.warning(self, 'Error', 'You must be connected to '
                                'a daemon to be able to select devices.')
            return
        dlg = DevicesDialog(self, self.measdef, self.client)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        self.measdef.devices = dlg.toDefs()
        self.updateTable()

    @pyqtSlot(str)
    def on_outerLoop_currentTextChanged(self, oloop):
        self.middleLoop.clear()
        for loop in LOOPS:
            if loop != oloop:
                self.middleLoop.addItem(loop)
        self.middleLoop.setCurrentIndex(0)

    @pyqtSlot(str)
    def on_middleLoop_currentTextChanged(self, mloop):
        oloop = self.outerLoop.currentText()
        self.innerLoop.clear()
        for loop in LOOPS:
            if loop not in (mloop, oloop):
                self.innerLoop.addItem(loop)
                self.measdef.loops = [oloop, mloop, loop]
                if mloop:
                    self.updateTable()
                break
        self.innerLoop.setCurrentIndex(0)

    def on_client_experiment(self, data):
        # reset everything
        self.rtBox.setChecked(False)
        self._clearTable()

    def on_rtBox_toggled(self, state):
        self.rtConfBtn.setEnabled(state)
        self._clearTable()

    def _clearTable(self):
        self.measdef = self.meas_def_class(self.rtBox.isChecked(), self.measdef.loops)
        self.updateTable()

    @pyqtSlot()
    def on_rtConfBtn_clicked(self):
        dlg = RtConfigDialog(self)
        dlg.setSettings(self.rt_settings)
        if not dlg.exec():
            return
        self.rt_settings = dlg.getSettings()

    def getValues(self):
        return {}

    def setValues(self, values):
        pass

    def updateTable(self):
        self.table.setRowCount(0)
        table = self.measdef.getTable()
        if not table:
            return
        first = table[0]
        self.table.setRowCount(len(table))
        self.table.setColumnCount(len(first))
        self.table.setHorizontalHeaderLabels(first.keys())
        total_time = 0
        for i, entry in enumerate(table):
            for j, element in enumerate(entry.values()):
                item = QTableWidgetItem(element.getDispValue())
                self.table.setItem(i, j, item)
                if element.eltype == 'time':
                    total_time += element.getValue()
        self.table.resizeRowsToContents()
        if self.rtBox.isChecked():
            total_time = self.rt_settings['totaltime'] * len(table)
        self.totalTime.setText(formatDuration(total_time))
        self.changed()

    def generate(self):
        out = []
        if self.measdef.samplefile is not None:
            out.append('run(%r)' % self.measdef.samplefile)
            out.append('')
        if self.rtBox.isChecked():
            out.append('SetupRealtime(%d, %d, %f, %r)' % (
                self.rt_settings['channels'],
                self.rt_settings['interval'] * (10 **
                {0: 0, 1: 3, 2: 6}[self.rt_settings['intervalunit']]),
                self.rt_settings['progq'],
                self.rt_settings['trigger'],
            ))
        else:
            out.append('SetupNormal()')
        table = self.measdef.getTable()
        # detect if we use a non-default value for these, and generate the
        # keywords only for these cases
        has_lenses = False
        has_chopper = False
        has_polarizer = False
        maxlen = {}
        for entry in table:
            for (k, v) in entry.items():
                vrepr = repr(v.getValue())
                maxlen[k] = max(maxlen.get(k, 0), len(vrepr))
                if k == 'chopper' and v.getValue() != 'off':
                    has_chopper = True
                elif k == 'polarizer' and v.getValue() != 'out':
                    has_polarizer = True
                elif k == 'lenses' and v.getValue() != 'out-out-out':
                    has_lenses = True
        for entry in table:
            items = []
            for (k, v) in entry.items():
                if k == 'chopper' and not has_chopper:
                    continue
                if k == 'polarizer' and not has_polarizer:
                    continue
                if k == 'lenses' and not has_lenses:
                    continue
                items.append('%s=%-*r' % (k, maxlen[k], v.getValue()))
            out.append('kwscount(' + ', '.join(items) + ')')
        return '\n'.join(out)


register(MeasureTable)
