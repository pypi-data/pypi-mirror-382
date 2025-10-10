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

from math import cos, radians, sin

from nicos.clients.gui.panels.generic import GenericPanel
from nicos.guisupport.qt import QBrush, QColor, QPainter, QPen, Qt, QWidget, \
    pyqtSlot
from nicos.guisupport.widget import NicosWidget
from nicos.protocols.cache import cache_load

OUT_WIDTH  = 22
IN_WIDTH = 36
SEG_ANGLE = 11
EXTRA_SEG_ANGLE = 15
MAX_SEGS = 10
MAX_ANGLE = 180

# (bit, invert, phi, r, talign, text)
SWITCHES = [
    # bits from diagnostics
    (0,  False, +35,  870, 2, 'Leak CW'),
    (1,  False, -35,  870, 1, 'Leak CCW'),
    (2,  False, +15,  700, 2, 'Max MB change CW'),
    (3,  False, +12,  770, 2, 'Min MB change CW'),
    (4,  True,  +10,  820, 2, 'Block in beam CW'),
    (5,  True, -10,  820, 1, 'Block in beam CCW'),
    (6,  False, -12,  770, 1, 'Min MB change CCW'),
    (7,  False, -15,  700, 1, 'Max MB change CCW'),
    (8,  False, 180,  500, 2, 'Emergency stop'),
    (9,  False, 180,  600, 2, 'Compr. Air OK'),
    (10, False, 0,    800, 3, 'MB arm mid'),
    (11, False, +15,  450, 2, 'Arm Klinke CW'),
    (12, False, -15,  450, 1, 'Arm Klinke CCW'),
    # bits from diag_switches
    (16, False, +30,  400, 2, 'Limit Arm CW'),
    (17, False, -30,  400, 1, 'Limit Arm CCW'),
    (18, False, -25,  425, 1, 'Ref Arm'),
    (19, False, -245, 880, 2, 'Limit MTT CW'),
    (20, False, -205, 880, 2, 'Limit MTT CCW'),
    (21, False, -200, 880, 2, 'Ref MTT'),
]


class MonoBlocks(NicosWidget, QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

        self.p_black = QPen(QColor('black'))
        self.p_red = QPen(QColor('red'))

        self.br_back = QBrush(QColor(190, 190, 190))
        self.br_empty = QBrush(QColor(255, 255, 255))

        self.col_led = [QColor(0, 0, 255), QColor(255, 255, 0)]
        self.br_led = [QBrush(self.col_led[0]), QBrush(self.col_led[1])]
        self.br_seg = QBrush(QColor(211, 211, 211))

        self.devs = ['diagnostics/value', 'diag_switches/value',
                     'mb_arm_raw/value', 'mtt_raw/value', 'n_blocks_cw/value']
        self.values = [0, 0, 0, 0, 0]

    def registerKeys(self):
        for dev in self.devs:
            self.registerKey(dev)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.values[self.devs.index(dev)] = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = painter.window()
        dia = min(rect.width(), rect.height()) - 40
        if dia <= 0:
            return
        dia_in = int(dia * 4/9.)

        painter.setPen(self.p_black)
        painter.setWindow(-dia/2, -dia/2, dia, dia)
        v = painter.viewport()
        painter.setViewport(v.left() + (v.width() - dia)/2,
                            v.top() + (v.height() - dia)/2,
                            dia, dia)

        # outer circle
        painter.setBrush(self.br_back)
        painter.drawEllipse(-dia//2, -dia//2, dia, dia)
        # incoming beam
        painter.setBrush(self.br_empty)
        painter.drawPie(-dia//2, -dia//2, dia, dia,
                        16*(90 - IN_WIDTH//2), 16*IN_WIDTH)

        painter.setBrush(self.br_seg)
        start = IN_WIDTH / 2 + 90
        for _ in range(MAX_SEGS - self.values[4]):
            painter.drawPie(-dia//2, -dia//2, dia, dia, 16*start, 16*SEG_ANGLE)
            start += SEG_ANGLE

        painter.setBrush(self.br_empty)
        painter.drawPie(-dia//2, -dia//2, dia, dia, 16*start, 16*OUT_WIDTH)

        painter.setBrush(self.br_seg)
        start = -IN_WIDTH / 2 + 90
        for _ in range(self.values[4]):
            painter.drawPie(-dia//2, -dia//2, dia, dia, 16*start, -16*SEG_ANGLE)
            start -= SEG_ANGLE

        # inner circle
        painter.drawEllipse(-dia_in//2, -dia_in//2, dia_in, dia_in)

        # outgoing beam (mtt angle)
        painter.drawLine(0, -dia//2, 0, 0)
        painter.rotate(self.values[3])
        painter.drawLine(0, 0, 0, dia//2)
        painter.rotate(-self.values[3])

        # mobil arm angle
        painter.setPen(self.p_red)
        painter.rotate(self.values[2])
        painter.drawLine(0, 0, 0, -(dia + dia_in)//4)
        painter.rotate(-self.values[2])
        painter.setPen(self.p_black)

        # switches
        swvals = self.values[0] | self.values[1] << 16
        for (bit, invert, phi, r, talign, text) in SWITCHES:
            on = (swvals & (1 << bit) != 0) ^ invert
            r = (r / 1800) * dia
            posx = round(r * cos(radians(phi - 90)))
            posy = round(r * sin(radians(phi - 90)))
            painter.setBrush(self.br_led[on])
            painter.drawEllipse(posx - 5, posy - 5, 10, 10)
            if talign == 1:
                painter.drawText(posx - 210, posy - 5, 200, 20,
                                 Qt.AlignmentFlag.AlignRight |
                                 Qt.AlignmentFlag.AlignTop, text)
            elif talign == 2:
                painter.drawText(posx + 10, posy - 5, 200, 20,
                                 Qt.AlignmentFlag.AlignLeft |
                                 Qt.AlignmentFlag.AlignTop, text)
            else:
                painter.drawText(posx - 100, posy - 20, 200, 20,
                                 Qt.AlignmentFlag.AlignHCenter |
                                 Qt.AlignmentFlag.AlignTop, text)


class MTTManualPanel(GenericPanel):

    panelName = 'MTT_Manual'

    def __init__(self, parent, client, options):
        options['uifile'] = 'nicos_mlz/panda/gui/mtt_manual.ui'
        GenericPanel.__init__(self, parent, client, options)
        self.monowidget = MonoBlocks(self)
        self.monowidget.setClient(self.client)
        self.graphicsWidget.layout().addWidget(self.monowidget)
        self._curmode = client.eval('opmode()')
        client.cache.connect(self.on_client_cache)

    def on_client_cache(self, data):
        (_, key, _, value) = data
        if key == 'opmode/value' and value:
            self._curmode = cache_load(value)

    @pyqtSlot()
    def on_modeOn_clicked(self):
        self.client.run('maw("opmode", "manual mode")')

    @pyqtSlot()
    def on_modeOff_clicked(self):
        self.client.run('maw("opmode", "automatic mode")')

    def _run_if_manual(self, code):
        if self._curmode != 'manual mode':
            self.showError('You need to activate manual mode first.')
        else:
            self.client.run(code)

    def on_mttEdit_valueChosen(self, val):
        self._run_if_manual('move("mtt_raw", %r)' % val)

    def on_mbEdit_valueChosen(self, val):
        self._run_if_manual('move("mb_arm_raw", %r)' % val)

    @pyqtSlot()
    def on_mttStop_clicked(self):
        self._run_if_manual('stop("mtt_raw")')

    @pyqtSlot()
    def on_mbStop_clicked(self):
        self._run_if_manual('stop("mb_arm_raw")')

    @pyqtSlot()
    def on_mttReset_clicked(self):
        self._run_if_manual('reset("mtt_raw")')

    @pyqtSlot()
    def on_mbReset_clicked(self):
        self._run_if_manual('reset("mb_arm_raw")')

    @pyqtSlot()
    def on_magOn_clicked(self):
        self._run_if_manual('maw("mb_arm_magnet", "on")')

    @pyqtSlot()
    def on_magOff_clicked(self):
        self._run_if_manual('maw("mb_arm_magnet", "off")')

    @pyqtSlot()
    def on_ccwOn_clicked(self):
        self._run_if_manual('maw("klinke_ccw", "on")')

    @pyqtSlot()
    def on_ccwOff_clicked(self):
        self._run_if_manual('maw("klinke_ccw", "off")')

    @pyqtSlot()
    def on_cwOn_clicked(self):
        self._run_if_manual('maw("klinke_cw", "on")')

    @pyqtSlot()
    def on_cwOff_clicked(self):
        self._run_if_manual('maw("klinke_cw", "off")')
