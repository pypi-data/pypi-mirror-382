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
#   Lydia Fleischhauer-Fuß <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI PIN diode single detectors"""

import time

from nicos import session
from nicos.core import Value, status
from nicos.core.device import Measurable, Moveable
from nicos.core.params import Attach, Param
from nicos.devices.entangle import AnalogInput, DigitalInput, NamedDigitalInput


class SingleDetectors(Measurable):

    attached_devices = {
        'pintimer': Attach('Time for pin measurement', Moveable),
        'pinstate': Attach('Status for pin measurement', NamedDigitalInput),
        'pincontrol': Attach('Status control for pin measurement', DigitalInput),
        'pindiodes': Attach('Integrated pindiodes', AnalogInput, multiple=5),
    }

    parameters = {
        'detector': Param('Detector used for timing', type=str,
                          default='pilatus'),
    }

    def doInit(self, mode):
        self.log.debug('Integral init')
        self._preset = 0
        self._timeout = 3

    def presetInfo(self):
        return ['t']

    def doSetPreset(self, **presets):
        self.log.debug('Integral set preset')
        if 't' in presets:
            self._preset = presets['t']
        self._lastpreset = presets

    def valueInfo(self):
        return tuple(Value(
            pd.name, type='counter', unit=pd.unit,
            fmtstr=pd.fmtstr,
        ) for pd in self._attached_pindiodes)

    def doRead(self, maxage=0):
        self.log.debug('Integral read')
        values = [int(dev.read(0)) for dev in self._attached_pindiodes]
        return values

    def doPrepare(self):
        self.log.debug('Pindiode prepare')
        timeval = time.time() + self._timeout
        if self.detector not in session.experiment.detlist:
            self._attached_pintimer.start(0)
            while self._attached_pincontrol.read(0) != 1:
                if time.time() > timeval:
                    self.log.warning('Pinstate timeout in prepare')
                    return
                session.delay(0.02)

    def doStart(self):
        self.log.debug('Integral start')
        timeval = time.time() + self._timeout
        if self.detector not in session.experiment.detlist:
            self._attached_pintimer.start(self._preset)
        while self.status(0)[0] != status.BUSY:
            if time.time() > timeval:
                self.log.warning('Pinstate timeout in start')
                return
            session.delay(0.02)

    def doStop(self):
        self.log.debug('Pintimer stop')
        self._attached_pintimer.start(0)

    def doFinish(self):
        pass

    def doReset(self):
        self.log.debug('Pintimer reset')
        self._attached_pintimer.start(0)

    def doStatus(self, maxage=0):
        self.log.debug('Integral status')
        timeval = time.time() + self._timeout
        state = self._attached_pinstate.read(0)
        self._attached_pintimer.poll()
        if state == 'counting':
            if time.time() > (timeval + self._preset):
                return status.ERROR, 'Timeout in PIN diode device.'
            return status.BUSY, 'The device is in MOVING state.'
        return status.OK, 'The device is in ON state.'
