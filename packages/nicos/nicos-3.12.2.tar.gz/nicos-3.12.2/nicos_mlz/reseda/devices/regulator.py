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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import time

from nicos import session
from nicos.core import POLLER, Attach, Moveable, NicosError, Override, Param, \
    Readable, none_or, status, tupleof
from nicos.utils import createThread


class Regulator(Moveable):
    """Regulate an attached moveable by monitoring an attached readable.

    Will be used for monitoring and regulating the amplitude of the
    frequency generators for the resonating circuits.

    The regulation is done, assuming that the movable is (approximately)
    directly proportional to the sensor."""

    attached_devices = {
        'moveable': Attach('Device to regulate', Moveable),
        'sensor': Attach('Device to evaluate', Readable),
    }

    parameters = {
        'stepfactor': Param('Factor of regulation steps', type=float,
                            settable=True, mandatory=False, default=0.5),
        'minstep': Param('Minimum stepsize if adjusting', type=float,
                         settable=True, mandatory=False, default=0.001),
        'deadbandwidth': Param('Width of the dead band', type=float,
                               settable=True, mandatory=False, default=0.05),
        'loopdelay': Param('Sleep time when waiting', type=float, unit='s',
                           default=1.0, settable=True),
        'maxstep': Param('Maximum step size', type=none_or(float),
                         settable=True,
                         mandatory=False, default=None),
        'curstatus': Param('Store the current device status',
                           internal=True, type=tupleof(int, str),
                           settable=True),
    }

    parameter_overrides = {
        'unit': Override(default='', settable=False, mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        self._regulation_thread = None
        self._stop_request = False
        self.valuetype = self._attached_moveable.valuetype

    def doShutdown(self):
        self.doStop()

    def doStart(self, target):
        self._stop_request = False
        if self._regulation_thread is None and session.sessiontype != POLLER:
            # no regulation thread (yet), but running in daemon -> start one
            self._regulation_thread = createThread('regulation thread %s' % self,
                                                   self._regulate)
        self.curstatus = status.BUSY, 'regulating'
        self.poll()

    def doStop(self):
        self._stop_request = True
        if self._regulation_thread:
            self._regulation_thread.join()
            self.poll()

    def doRead(self, maxage=0):
        return self._attached_sensor.read(maxage)

    def doStatus(self, maxage=0):
        if session.sessiontype != POLLER:  # XXX!
            if self._regulation_thread and self._regulation_thread.is_alive():
                # self.curstatus = status.BUSY, 'regulating'
                pass
            else:
                self.curstatus = status.OK, 'idle'
        return self.curstatus

    def _regulate(self):
        while not self._stop_request:
            try:
                read_val = self._attached_sensor.read(0)
                self.log.debug('Readable value: %s', read_val)

                diff = abs(self.target - read_val)
                self.log.debug('Difference to the target: %s', diff)
                if diff > self.deadbandwidth:
                    self.curstatus = status.BUSY, 'regulating'
                if diff > self.deadbandwidth / 2:
                    cur_write_val = self._attached_moveable.read(0)
                    step = self.stepfactor * (diff - self.deadbandwidth / 2)
                    step = max(step, self.minstep)
                    maxstep = self.maxstep or step
                    sign = 1 if read_val < self.target else -1

                    step = min(step, maxstep) * sign
                    new_target = cur_write_val + step

                    self.log.debug('Regulation necessary, move attached movable:'
                                   '%s -> %s', cur_write_val, new_target)

                    if hasattr(self._attached_moveable, 'absmax'):
                        new_target = min(new_target,
                                         self._attached_moveable.absmax)
                    if hasattr(self._attached_moveable, 'usermax'):
                        new_target = min(new_target,
                                         self._attached_moveable.usermax)

                    self._attached_moveable.start(new_target)
                    # TODO: wait?
                else:
                    self.curstatus = status.OK, 'stable'

            except NicosError as e:
                self.log.warning('Skip regulation: %s', e)

            time.sleep(self.loopdelay)
        self._regulation_thread = None
        self._stop_request = False
