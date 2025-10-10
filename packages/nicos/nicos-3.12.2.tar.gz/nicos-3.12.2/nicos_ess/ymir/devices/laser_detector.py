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
#   Matt Clarke <matt.clarke@ess.eu>
#   Ebad Kamil <ebad.kamil@ess.eu>
#   Jonas Petersson <jonas.petersson@ess.eu>
#
# *****************************************************************************
import time

from nicos import session
from nicos.core import Param, Value, multiStatus, status, tupleof
from nicos.core.constants import LIVE
from nicos.core.device import Measurable, Readable
from nicos.core.params import Attach
from nicos.devices.epics.pva import EpicsReadable
from nicos.utils import createThread


class TimingStatusDevice(EpicsReadable):
    def doRead(self, maxage=0):
        return ''

    def doStatus(self, maxage=0):
        try:
            severity, msg = self.get_alarm_status('readpv')
            # Check if there are issues with the device
            if severity in [status.ERROR, status.WARN]:
                return severity, f'PV alarm: {msg}'
            # If the device is running, look for timestamp synch issues
            if self._get_pv('readpv') == 0:
                return status.WARN, ('Timing warning: the timestamps appear '
                                     'to have lost synchronisation.')
            return status.OK, 'the timestamps are synchronised.'
        except TimeoutError:
            return status.ERROR, 'timeout reading status'


class LaserDetector(Measurable):
    parameters = {
        'answer':
            Param('Store the iterative average of the attached device value',
                  internal=True,
                  type=float,
                  default=0,
                  settable=True),
        'curstatus':
            Param('Store the current device status',
                  internal=True,
                  type=tupleof(int, str),
                  default=(status.OK, 'idle'),
                  settable=True)
    }

    attached_devices = {
        'laser': Attach('the underlying laser device', Readable),
        'timingstatus': Attach('timestamp synchronisation status device',
                               Readable),
    }

    _stoprequest = False
    _counting_worker = None

    def doPrepare(self):
        self.curstatus = status.OK, 'idle'

    def doStart(self):
        self._stoprequest = False
        self.curstatus = status.BUSY, 'Counting'
        self._counting_worker = createThread(
            'start_counting', self._start_counting,
            args=(self._lastpreset.get('t', None), ))

    def _start_counting(self, duration=None):
        max_pow = 0
        counter = 0
        value = 0

        count_until = None
        if duration:
            count_until = time.monotonic() + duration
        while not self._stoprequest:
            session.delay(0.1)
            max_pow = max(self._attached_laser.read(), max_pow)
            counter += 1
            value += max_pow
            self.answer = value / counter  # iterative average
            if count_until and time.monotonic() > count_until:
                break
        self.curstatus = status.OK, 'idle'

    def doRead(self, maxage=0):
        return [self.answer]

    def doFinish(self):
        self._stop_processing()

    def doSetPreset(self, **preset):
        self.curstatus = status.BUSY, 'Preparing'
        self._lastpreset = preset

    def doStop(self):
        self._stoprequest = True
        self._stop_processing()

    def _stop_processing(self):
        self._cleanup_worker()
        self.curstatus = status.OK, 'idle'

    def _cleanup_worker(self):
        if self._counting_worker and self._counting_worker.is_alive():
            self._counting_worker.join()
        self._counting_worker = None

    def doStatus(self, maxage=0):
        highest_severity, msg = multiStatus(self._adevs, maxage)
        if highest_severity != status.OK:
            return highest_severity, msg
        return self.curstatus

    def duringMeasureHook(self, elapsed):
        return LIVE

    def valueInfo(self):
        return Value(self.name, unit=self.unit),
