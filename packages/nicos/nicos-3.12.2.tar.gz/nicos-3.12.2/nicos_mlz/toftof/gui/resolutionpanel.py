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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from numpy import array

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.core.errors import NicosError
from nicos.core.utils import ADMIN
from nicos.guisupport.livewidget import LiveWidget1D
from nicos.guisupport.plots import GRCOLORS, MaskedPlotCurve
from nicos.guisupport.qt import QDialogButtonBox, QDoubleValidator, QLabel, \
    QMessageBox, QSize, QSizePolicy, Qt, QVBoxLayout, QWidget, pyqtSlot
from nicos.guisupport.utils import waitCursor
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import findResource

from nicos_mlz.toftof.lib.calculations import ResolutionAnalysis

COLOR_BLACK = GRCOLORS['black']
COLOR_RED = GRCOLORS['red']
COLOR_GREEN = GRCOLORS['green']
COLOR_BLUE = GRCOLORS['blue']

ANGSTROM = '\u212b'
DELTA = '\u0394'
LAMBDA = '\u03bb'
MICRO = '\xb5'
MINUSONE = '\u207b\xb9'


class MiniPlot(LiveWidget1D):

    client = None

    def __init__(self, xlabel, ylabel, ncurves=1, parent=None, **kwds):
        LiveWidget1D.__init__(self, parent, **kwds)

        self.axes.resetCurves()
        self.setTitles({'x': xlabel, 'y': ylabel})

        self._curves = [
            MaskedPlotCurve([0], [1], linewidth=2, legend='',
                            linecolor=kwds.get('color1', COLOR_BLACK)),
            MaskedPlotCurve([0], [.1], linewidth=2, legend='',
                            linecolor=kwds.get('color2', COLOR_GREEN)),
        ]
        for curve in self._curves[:ncurves]:
            self.axes.addCurves(curve)
        self.plot.setLegend(True)
        # Disable creating a mouse selection to zoom
        self.gr.setMouseSelectionEnabled(False)

    def sizeHint(self):
        return QSize(120, 120)

    def reset(self):
        self.plot.reset()


class PlotWidget(QWidget):

    def __init__(self, title, xlabel, ylabel, ncurves=1, name='unknown',
                 parent=None, **kwds):
        QWidget.__init__(self, parent)
        self.name = name
        parent.setLayout(QVBoxLayout())
        self.plot = MiniPlot(xlabel, ylabel, ncurves, self, color1=COLOR_BLUE,
                             color2=COLOR_RED, **kwds)
        titleLabel = QLabel(title)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setStyleSheet('QLabel {font-weight: 600}')
        parent.layout().insertWidget(0, titleLabel)
        self.plot.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                                QSizePolicy.Policy.MinimumExpanding)
        parent.layout().insertWidget(1, self.plot)

    def setData(self, x, y1, y2=None):
        for curve, y in zip(self.plot._curves, (y1, y2)):
            if y is not None:
                curve.x = array(x)
                curve.y = array(y)

        self.plot.reset()
        self.plot.update()


class DynamicRangePlot(PlotWidget):

    def __init__(self, parent, **kwds):
        PlotWidget.__init__(self, 'Dynamic Range', DELTA + 'E (meV)',
                            '|Q| ' + ANGSTROM + MINUSONE, 2, parent=parent,
                            **kwds)
        self.plot._curves[0].legend = 'low'
        self.plot._curves[1].legend = 'high'


class ElasticResolutionPlot(PlotWidget):

    def __init__(self, parent, **kwds):
        PlotWidget.__init__(self, 'Elastic Resolution',
                            LAMBDA + '(' + ANGSTROM + ')',
                            'dE (' + MICRO + 'eV)', 1, parent=parent, **kwds)
        self.plot.logscale(True)


class ResolutionPlot(PlotWidget):

    def __init__(self, parent, **kwds):
        PlotWidget.__init__(self, 'Resolution', 'Energy (meV)',
                            'dE (' + MICRO + 'eV)', 1, parent=parent, **kwds)
        self.plot.logscale(True)


class ResolutionPanel(NicosWidget, Panel):

    ch_dev = PropDef('ch_dev', str, 'ch', 'Chopper device')
    speed_dev = PropDef('speed_dev', str, 'chSpeed', 'Chopper speed device')
    wl_dev = PropDef('wl_dev', str, 'chWL', 'Wavelength device')
    ratio_dev = PropDef('ratio_dev', str, 'chRatio', 'Chopper ratio device')
    st_dev = PropDef('st_dev', str, 'chST', 'Slittype device')

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        NicosWidget.__init__(self)
        self.setClient(client)
        client.connected.connect(self.on_client_connected)
        self.destroyed.connect(self.on_destroyed)
        if parent:
            self.buttonBox.rejected.connect(parent.close)
        else:
            self.buttonBox.rejected.connect(self.close)

        self.speed.valueChanged['double'].connect(self.recalculate)
        self.waveLength.valueChanged['double'].connect(self.recalculate)
        self.ratio.valueChanged['int'].connect(self.recalculate)
        self.slits.currentIndexChanged.connect(self.recalculate)
        self.buttonBox.clicked.connect(self.createScript)
        self.slits.setDisabled(self.client.user_level != ADMIN)

    def on_destroyed(self):
        pass

    def initUi(self):
        with waitCursor():
            loadUi(self,
                   findResource('nicos_mlz/toftof/gui/resolutionpanel.ui'))

            valid = QDoubleValidator()

            for f in (self.E_neutron, self.Q0_min, self.Q0_max, self.dE_max,
                      self.dE_el):
                f.setValidator(valid)
                f.setReadOnly(True)

            self.plot1 = DynamicRangePlot(self.drPlot, xscale='decimal')
            self.plot2 = ElasticResolutionPlot(self.erPlot, xscale='decimal')
            self.plot3 = ResolutionPlot(self.rPlot, xscale='decimal')

    def registerKeys(self):
        for dev in (self.speed_dev, self.wl_dev):
            self.registerKey(f'{dev}/abslimits')

    def on_client_connected(self):
        with waitCursor():
            missed_devices = []
            for d in (self.speed_dev, self.ratio_dev,
                      self.wl_dev, self.st_dev):
                try:
                    self.client.eval(f'{d}.pollParams()', None)
                    params = self.client.getDeviceParams(d)
                    for p, v in params.items():
                        self._update_key('%s/%s' % (d, p), v)
                except (NicosError, NameError):
                    missed_devices += [d]
            vt = self._client.getDeviceValuetype(self.ratio_dev)
            self.ratio.setRange(min(vt.vals), max(vt.vals))
        if not missed_devices:
            self.recalculate()
        else:
            QMessageBox.warning(self.parent().parent(), 'Error',
                                'The following devices are not available:<br>'
                                "'%s'" % ', '.join(missed_devices))
            self.buttonBox.removeButton(
                self.buttonBox.button(QDialogButtonBox.StandardButton.Apply))

    def on_keyChange(self, key, value, time, expired):
        dev, param = key.split('/')
        if param == 'abslimits':
            if dev == self.speed_dev.lower():
                self.speed.setRange(*value)
            elif dev == self.wl_dev.lower():
                self.waveLength.setRange(*value)
        NicosWidget.on_keyChange(self, key, value, time, expired)

    def _update_key(self, key, value):
        if key in [f'{self.speed_dev}/value', f'{self.ch_dev}/speed']:
            self.speed.setValue(value if value else 3000)
        elif key in [f'{self.ratio_dev}/value', f'{self.ch_dev}/ratio']:
            self.ratio.setValue(int(value))
        elif key in [f'{self.wl_dev}/value', f'{self.ch_dev}/wavelength']:
            self.waveLength.setValue(float(value))
        elif key in [f'{self.st_dev}/value', f'{self.ch_dev}/slittype']:
            self.slits.setCurrentIndex(int(value))

    @pyqtSlot()
    def recalculate(self):
        try:
            self._simulate()
        except (ZeroDivisionError, IndexError):
            QMessageBox.warning(self.parent().parent(), 'Error',
                                'The current instrument setup is not well '
                                'defined for polarisation analysis')

    @pyqtSlot('QAbstractButton *')
    def createScript(self, button):
        if self.buttonBox.standardButton(button) \
                == QDialogButtonBox.StandardButton.Apply:
            maw = [f'{self.wl_dev}, %.2f' % self.waveLength.value()]
            maw.append(f'{self.ratio_dev}, %d' % self.ratio.value())
            maw.append(f'{self.speed_dev}, %d' % self.speed.value())
            s = ['maw(%s)' % ', '.join(maw)]
            if self.client.user_level == ADMIN:
                s.append(f'maw({self.st_dev}, %d)' % self.slits.currentIndex())
            script = '\n'.join(s)
            # print(script)
            self.client.run(script, noqueue=False)

    def _simulate(self):
        """Calculate
        """
        ra = ResolutionAnalysis(
            self.speed.value(), self.waveLength.value(), self.ratio.value(),
            self.slits.currentIndex())
        ra.run()

        self.E_neutron.setText('%.4f' % ra.E0)
        self.Q0_min.setText('%.4f' % ra.q_low_0)
        self.Q0_max.setText('%.4f' % ra.q_high_0)
        self.dE_max.setText('%.4f' % -ra.dE_min)
        self.dE_el.setText('%.4f' % ra.dE_el)

        self.plot1.setData(-ra.dE, ra.q_low, ra.q_high)
        self.plot2.setData(ra.lambdas, 1e3 * ra.dE_res)
        self.plot3.setData(-1. * ra.dE, 1e3 * ra.dE_in)
