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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Attenuator class for PUMA."""

from nicos import session
from nicos.core import SIMULATION, Attach, HasLimits, Moveable, NicosError, \
    Readable, status


class Attenuator(HasLimits, Moveable):
    """Puma specific attenuator."""

    # XXX rework this as it is basically a MultiSwitcher with a blocking start

    attached_devices = {
        'io_status': Attach('readout for the status', Readable),
        'io_set': Attach('output to set', Moveable),
        'io_press': Attach('...', Readable),
    }

    hardware_access = False

    def doInit(self, mode):
        self._filterlist = [1, 2, 5, 10, 20]
        self._filmax = sum(self._filterlist)

        if mode == SIMULATION:
            return
        stat1 = self._attached_io_status.read()
        stat2 = 0
        for i in range(0, 5):
            stat2 += (((stat1 >> (2 * i + 1)) & 1) << i)
        self._attached_io_set.move(stat2)
        self.log.debug('device status read from hardware: %s', stat1)
        self.log.debug('device status sent to hardware: %s', stat2)

    def doStart(self, target):
        try:
            actpos = target
            if target == self.read(0):
                return
            if target > self._filmax:
                self.log.info('exceeding maximum filter thickness; '
                              'switch to maximum %d %s',
                              self._filmax, self.unit)
                target = self._filmax

            if self.doStatus()[0] == status.ERROR:
                raise NicosError(self, 'inconsistency of attenuator status, '
                                 'check device!')

            # if self.io_press == 0:
            #     msg = 'no air pressure; cannot move attenuator'
            #     raise DeviceUndefinedError(msg)
            result = 0
            temp = 0
            for i in range(4, -1, -1):
                temp = (target - target % self._filterlist[i])
                if temp > 0:
                    result += 2**i
                    target -= self._filterlist[i]

                self.log.debug('position: %d, temp: %d result: %d, '
                               'filterlist[i]: %d',
                               target, temp, result, self._filterlist[i])
            self._attached_io_set.move(result)
            session.delay(3)

            if self.doStatus()[0] != status.OK:
                raise NicosError(self, 'attenuator returned wrong position')

            if self.read(0) < actpos:
                self.log.info('requested filter combination not possible; '
                              'switched to %r %s thickness:',
                              self.read(), self.unit)
        finally:
            self.log.info('new attenuation: %s %s', self.read(), self.unit)

    def doRead(self, maxage=0):
        if self.doStatus()[0] == status.OK:
            result = 0
            fil = 0
            readvalue = self._attached_io_status.read(maxage)
            for i in range(0, 5):
                fil = (readvalue >> (i * 2 + 1)) & 1
                self.log.debug('filterstatus of %d: %d', i, fil)
                if fil == 1:
                    result += self._filterlist[i]
            return result
        else:
            raise NicosError(self, 'device undefined; check it!')

    def doReset(self):
        self.start(0)

    def doStatus(self, maxage=0):
        stat1 = self._attached_io_set.read(maxage)
        checkstatus = self._checkstatus(maxage)
        stat2 = checkstatus[0] + checkstatus[1]
        stat3 = checkstatus[0]
        if (abs(stat1 - stat3) == 0) and stat2 == 31:
            return (status.OK, 'idle')
        else:
            return (status.ERROR, 'device undefined, please check')

    def _checkstatus(self, maxage=0):
        stat1 = self._attached_io_status.read(maxage)
        stat2 = 0
        stat3 = 0
        for i in range(5):
            stat2 += (((stat1 >> (2 * i + 1)) & 1) << i)
            stat3 += (((stat1 >> (2 * i)) & 1) << i)
            self.log.debug('%d, %d, %d', stat1, stat2, stat3)
        return (stat2, stat3)
