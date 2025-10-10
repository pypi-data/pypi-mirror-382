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

"""NICOS live 2D data plot window/panel."""

import os
from os import path

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QByteArray, QDialog, QDoubleSpinBox, \
    QFileDialog, QLabel, QListWidgetItem, QMenu, QPageLayout, QPrintDialog, \
    QPrinter, QSizePolicy, QStatusBar, Qt, QToolBar, pyqtSlot
from nicos.utils import findResource

try:
    from nicoscascadewidget import CascadeWidget, TmpImage
except ImportError:
    CascadeWidget = TmpImage = None


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_mlz/mira/gui/live.ui'))

        self._format = None
        self._runtime = 0
        self._no_direct_display = False
        self._range_active = False

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        if CascadeWidget:
            self.widget = CascadeWidget(self)
            self.widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.widgetLayout.addWidget(self.widget)
        else:
            raise RuntimeError('The Cascade live widget is not available')

        self.rangeFrom = QDoubleSpinBox(self)
        self.rangeTo = QDoubleSpinBox(self)
        for ctrl in [self.rangeFrom, self.rangeTo]:
            ctrl.setRange(0, 100000000)
            ctrl.setEnabled(False)
            ctrl.setMaximumWidth(90)
            ctrl.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed,
                                           QSizePolicy.Policy.Fixed))
            ctrl.valueChanged.connect(self.on_rangeChanged)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(32, '')
        self.liveitem.setData(33, '')

        self.splitter.setSizes([20, 80])
        self.splitter.restoreState(self.splitterstate)

        client.livedata.connect(self.on_client_livedata)
        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)

        self.actionLogScale.toggled.connect(self.widget.SetLog10)
        self.actionSelectChannels.triggered.connect(self.widget.showSumDlg)
        self.widget.customContextMenuRequested.connect(
            self.on_widget_customContextMenuRequested)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

    def getMenus(self):
        self.menu = menu = QMenu('&Live data', self)
        menu.addAction(self.actionLoadTOF)
        menu.addAction(self.actionLoadPAD)
        menu.addSeparator()
        menu.addAction(self.actionWriteXml)
        menu.addAction(self.actionPrint)
        menu.addSeparator()
        menu.addAction(self.actionSetAsROI)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionNormalized)
        menu.addAction(self.actionLegend)
        return [menu]

    def getToolbars(self):
        bar = QToolBar('Live data')
        bar.addAction(self.actionWriteXml)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionSetAsROI)
        bar.addSeparator()
        bar.addAction(self.actionSelectChannels)
        bar.addSeparator()
        bar.addAction(self.actionCustomRange)
        bar.addWidget(self.rangeFrom)
        bar.addWidget(QLabel(' to '))
        bar.addWidget(self.rangeTo)
        bar.addSeparator()
        bar.addAction(self.actionOverviewMode)
        bar.addAction(self.actionPhaseMode)
        bar.addAction(self.actionContrastMode)
        return [bar]

    def on_widget_customContextMenuRequested(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata'])
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath:
            return
        caspath = path.join(datapath, 'cascade')
        if path.isdir(caspath):
            for fn in sorted(os.listdir(caspath)):
                if fn.endswith('.pad'):
                    self.add_to_flist(path.join(caspath, fn), 'pad', False)
                elif fn.endswith('tof'):
                    self.add_to_flist(path.join(caspath, fn), 'tof', False)

    def on_client_livedata(self, params, blobs):
        tag, _uid, _det, filename, dtype, nx, ny, nt, runtime = params
        # TODO: remove compatibility code
        if not isinstance(filename, str):
            filename, nx, ny, nt = filename[0], nx[0], ny[0], nt[0]

        if dtype == '<u4' and nx == 128 and ny == 128 and tag != 'MiraXML':
            if nt == 1:
                self._format = 'pad'
            elif nt == 128:
                self._format = 'tof'
            self._runtime = runtime
            self._filename = filename
        else:
            if filename and tag != 'MiraXML':
                self._filename = filename
                self._format = filename[-3:]
            else:
                # print 'Unsupported live data format:', params
                self._format = None

        for blob in blobs:
            self._process_livedata(blob)

    def _process_livedata(self, data):
        if self._format not in ('pad', 'tof'):
            return
        if data:
            self._last_data = data
        if not self._no_direct_display and data:
            runtime = self._runtime or 1e-6
            if self._format == 'pad':
                self.widget.LoadPadMem(data, 128*128*4)
                cts = self.widget.GetPad().GetCounts()
                self.statusBar.showMessage('cps: %.2f | total: %s' %
                                           (cts/runtime, cts))
            else:
                self.widget.LoadTofMem(data, 128*128*128*4)
                cts = self.widget.GetTof().GetCounts()
                self.statusBar.showMessage('cps: %.2f | total: %s' %
                                           (cts/runtime, cts))
            self.updateRange()
        if self._filename and not self._filename.startswith(('live@', '<Live>@')):
            # and path.isfile(self._filename):
            if 'mira_cas' not in self._filename:
                self.add_to_flist(self._filename, self._format)

    def on_fileList_itemClicked(self, item):
        if item is None:
            return
        fname = item.data(32)
        fformat = item.data(33)
        if not fname:
            if self._no_direct_display:
                self._no_direct_display = False
                if self._format == 'pad':
                    self.widget.LoadPadMem(self._last_data, 128*128*4)
                    cts = self.widget.GetPad().GetCounts()
                    self.statusBar.showMessage('total: %s' % cts)
                elif self._format == 'tof':
                    self.widget.LoadTofMem(self._last_data, 128*128*128*4)
                    cts = self.widget.GetTof().GetCounts()
                    self.statusBar.showMessage('total: %s' % cts)
                self.updateRange()
        else:
            self._no_direct_display = True
            if fformat == 'pad':
                self.widget.LoadPadFile(fname)
                cts = self.widget.GetPad().GetCounts()
                self.statusBar.showMessage('total: %s' % cts)
            elif fformat == 'tof':
                self.widget.LoadTofFile(fname)
                cts = self.widget.GetTof().GetCounts()
                self.statusBar.showMessage('total: %s' % cts)
            self.updateRange()

    def on_fileList_currentItemChanged(self, item, previous):
        self.on_fileList_itemClicked(item)

    @pyqtSlot()
    def on_actionLoadTOF_triggered(self):
        filename = QFileDialog.getOpenFileName(self,
            'Open TOF File', '', 'TOF File (*.tof *.TOF);;All files (*)')[0]
        if filename:
            self.widget.LoadTofFile(filename)
            self.add_to_flist(filename, 'tof')

    @pyqtSlot()
    def on_actionLoadPAD_triggered(self):
        filename = QFileDialog.getOpenFileName(self,
            'Open PAD File', '', 'PAD File (*.pad *.PAD);;All files (*)')[0]
        if filename:
            self.widget.LoadPadFile(filename)
            self.updateRange()
            self.add_to_flist(filename, 'pad')

    def add_to_flist(self, filename, fformat, scroll=True):
        shortname = path.basename(filename)
        if self.fileList.count() > 2 and \
           self.fileList.item(self.fileList.count()-2).text() == shortname:
            return
        item = QListWidgetItem(shortname)
        item.setData(32, filename)
        item.setData(33, fformat)
        self.fileList.insertItem(self.fileList.count()-1, item)
        if scroll:
            self.fileList.scrollToBottom()

    @pyqtSlot()
    def on_actionWriteXml_triggered(self):
        pad = self.widget.GetPad()
        if pad is None:
            return self.showError('No 2-d image is shown.')
        filename = str(QFileDialog.getSaveFileName(
            self, 'Select file name', '', 'XML files (*.xml)')[0])
        if not filename:
            return
        if not filename.endswith('.xml'):
            filename += '.xml'
        if TmpImage:
            tmpimg = TmpImage()
            tmpimg.ConvertPAD(pad)
            tmpimg.WriteXML(filename)

    @pyqtSlot()
    def on_actionSetAsROI_triggered(self):
        zoom = self.widget.GetPlot().GetZoomer().zoomRect()
        self.client.run('psd_channel.roi = (%s, %s, %s, %s)' %
                        (int(zoom.left()), int(zoom.top()),
                         int(zoom.right()), int(zoom.bottom())))

    @pyqtSlot()
    def on_actionUnzoom_triggered(self):
        self.widget.GetPlot().GetZoomer().zoom(0)

    @pyqtSlot()
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setColorMode(QPrinter.ColorMode.Color)
        printer.setPageOrientation(QPageLayout.Orientation.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec() == QDialog.DialogCode.Accepted:
            self.widget.GetPlot().print_(printer)
        self.statusBar.showMessage('Plot successfully printed to %s.' %
                                   str(printer.printerName()))

    def on_actionCustomRange_toggled(self, on):
        self.rangeFrom.setEnabled(on)
        self.rangeTo.setEnabled(on)
        self.widget.SetAutoCountRange(not on)
        self._range_active = on
        if on:
            self.on_rangeChanged(0)
        else:
            self.updateRange()

    def on_rangeChanged(self, val):
        if self._range_active:
            self.widget.SetCountRange(self.rangeFrom.value(),
                                      self.rangeTo.value())

    def updateRange(self):
        if not self.actionCustomRange.isChecked():
            crange = self.widget.GetData2d().range()
            self.rangeFrom.setValue(crange.minValue())
            self.rangeTo.setValue(crange.maxValue())

    def closeEvent(self, event):
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())
        event.accept()

    @pyqtSlot()
    def on_actionOverviewMode_triggered(self):
        self.widget.viewOverview()

    @pyqtSlot()
    def on_actionPhaseMode_triggered(self):
        self.widget.SetFoil(7)
        self.widget.viewPhases()

    @pyqtSlot()
    def on_actionContrastMode_triggered(self):
        self.widget.SetFoil(7)
        self.widget.viewContrasts()
