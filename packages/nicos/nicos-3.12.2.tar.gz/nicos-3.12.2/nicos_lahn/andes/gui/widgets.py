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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************
"""Classes to display the Instrument."""

from math import cos, radians, sin

from nicos.core import status
from nicos.guisupport.elements import AnaTable, Beam, DetTable, MonoTable, \
    SampleTable, TableBase, TableTarget
from nicos.guisupport.qt import QGraphicsScene, QGraphicsView, QPainter


class InstrumentView(QGraphicsView):
    """Widget to visualise the current positions of the Instrument."""

    anaradius = 30
    monoradius = 40
    sampleradius = 20
    detectorradius = 10
    _beams = []

    # default values (used when no such devices are configured)
    values = {
        'mth': -45,
        'mtt': -90,
        'sth': 30,
        'stt': 60,
        'ath': -45,
        'att': -90,
        # scale the distances
        'Lms': 1000 / 10,
        'Lsa': 580 / 10,
        'LtoD': 400 / 10,
    }

    def __init__(self, parent=None, designMode=False):
        self.scene = QGraphicsScene(parent)
        QGraphicsView.__init__(self, self.scene, parent)
        self.setRenderHints(QPainter.Antialiasing)

        self.targets = self.values.copy()
        self.status = {
            'mth': status.OK,
            'mtt': status.OK,
            'sth': status.OK,
            'stt': status.OK,
            'ath': status.OK,
            'att': status.OK,
        }
        self._designMode = designMode

    def initUi(self, withAnalyzer=True):
        scene = self.scene
        self._mono = MonoTable(0., 0, self.monoradius, scene=scene)
        self._sample = SampleTable(0, 0, self.sampleradius, scene=scene)
        self._sample_t = TableTarget(0, 0, self.sampleradius, scene=scene)
        if withAnalyzer:
            self._ana = AnaTable(0, 0, self.anaradius, scene=scene)
            self._ana_t = TableTarget(0, 0, self.anaradius, scene=scene)
        self._det = DetTable(0, 0, self.detectorradius, scene=scene)
        self._det_t = TableTarget(0, 0, self.detectorradius, scene=scene)
        self._src = TableBase(0, 0, 0, scene=scene)
        self._src_beam = Beam(self._src, self._mono, scene=scene)
        self._mono_beam = Beam(self._mono, self._sample, scene=scene)
        if withAnalyzer:
            self._sample_beam = Beam(self._sample, self._ana, scene=scene)
            self._ana_beam = Beam(self._ana, self._det, scene=scene)
            self._beams = (self._src_beam, self._mono_beam, self._sample_beam, self._ana_beam)
        else:
            self._sample_beam = Beam(self._sample, self._det, scene=scene)
            self._beams = (self._src_beam, self._mono_beam, self._sample_beam)
        if self._designMode:
            self.update()

    def _getMaxL(self):
        ret = 0
        for x in self.distances:
            ret += self.values[x]
        return ret

    def resizeEvent(self, rsevent):
        s = self.size()
        w, h = s.width(), s.height()

        maxL = self._getMaxL()
        scale = min(w / (2 * (maxL + self.detectorradius)),
                    h / (maxL + self.monoradius + self.detectorradius))
        transform = self.transform()
        transform.reset()
        transform.scale(scale, scale)
        self.setTransform(transform)
        QGraphicsView.resizeEvent(self, rsevent)

    def beam(self):
        maxL = self._getMaxL()
        self._src.setPos(-(maxL - 3), 0)

    def monochromator(self):
        self._mono.setState(max(self.status['mth'], self.status['mtt']))
        self._mono.setPos(0, 0)
        self._mono.setRotation(self.values['mth'])

    def sample(self, sense):
        Lms = self.values['Lms']
        self.mtt = self.values['mtt']
        self.mttangle = sense * radians(self.mtt)
        self.mttangle_t = sense * radians(self.targets['mtt'])
        if self.values['mth'] < 0:
            self.mttangle = -self.mttangle
            self.mttangle_t = -self.mttangle_t

        self.sx, self.sy = Lms * cos(self.mttangle), -Lms * sin(self.mttangle)
        self.sx_t, self.sy_t = Lms * cos(self.mttangle_t), -Lms * sin(self.mttangle_t)
        self.sth = self.values['sth']
        self.stt = self.values['stt']

        self._sample_t.setPos(self.sx_t, self.sy_t)
        self._sample.setState(max(self.status['stt'], self.status['sth']))
        self._sample.setPos(self.sx, self.sy)
        self._sample.setRotation(self.sth - self.mtt + 45.)

    def analyzer(self):
        Lsa = self.values['Lsa']
        self.sttangle = radians(self.stt)
        self.sttangle_t = radians(self.targets['stt'])
        if self.sth < 0:
            self.sttangle = self.mttangle - self.sttangle
            self.sttangle_t = self.mttangle_t - self.sttangle_t
        else:
            self.sttangle = self.mttangle + self.sttangle
            self.sttangle_t = self.mttangle_t + self.sttangle_t
        self.ax, self.ay = self.sx + Lsa * cos(self.sttangle), self.sy - Lsa * sin(self.sttangle)
        self.ax_t, self.ay_t = self.sx_t + Lsa * cos(self.sttangle_t), \
                               self.sy_t - Lsa * sin(self.sttangle_t)
        ath = self.values['ath']

        self._ana_t.setPos(self.ax_t, self.ay_t)
        self._ana.setState(max(self.status['ath'], self.status['att']))
        self._ana.setPos(self.ax, self.ay)
        self._ana.setRotation(self.mtt + ath - self.stt)

    def analyzerToDetector(self):
        self._detector('att', 'ath', self.sttangle, self.sttangle_t,
                       self.ax, self.ay, self.ax_t, self.ay_t)

    def sampleToDetector(self):
        self._detector('stt', 'sth', self.mttangle, self.mttangle_t,
                       self.sx, self.sy, self.sx_t, self.sy_t)

    def _detector(self, xtt, xth, angle, angle_t, x, y, x_t, y_t):
        LtoD = self.values['LtoD']
        xttangle = radians(self.values[xtt])
        xttangle_t = radians(self.targets[xtt])
        if self.values[xth] < 0:
            xttangle = angle - xttangle
            xttangle_t = angle_t - xttangle_t
        else:
            xttangle = angle + xttangle
            xttangle_t = angle_t + xttangle_t

        dx, dy = x + LtoD * cos(xttangle), y - LtoD * sin(xttangle)
        dx_t, dy_t = x_t + LtoD * cos(xttangle_t), y_t - LtoD * sin(xttangle_t)
        self._det_t.setPos(dx_t, dy_t)
        self._det.setState(self.status[xtt])
        self._det.setPos(dx, dy)

    def updateBeams(self):
        # This call is needed to refresh drawing of the beams after moving
        # the tables
        for b in self._beams:
            b.update()

        QGraphicsView.update(self)
