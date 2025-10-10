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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Class for PUMA SR7 shutter control."""

from nicos.core import Attach, HasTimeout, Moveable, Override, PositionError, \
    Readable, oneof, status


class SR7Shutter(HasTimeout, Moveable):
    """Class for the PUMA secondary shutter."""

    attached_devices = {
        'sr7cl': Attach('status of SR7 shutter closed/open', Readable),
        'sr7p1': Attach('status of SR7 position 1', Readable),
        'sr7p2': Attach('status of SR7 position 2', Readable),
        'sr7p3': Attach('status of SR7 position 3', Readable),
        # 'hdiacl': Attach('status of virtual source closed/open',
        #                   Readable),
        # 'stopinh': Attach('status of emergency button active/inactive',
        #                   Readable),
        # 'sr7save': Attach('SR7 security circle ok for open the beam',
        #                   Readable),
        'sr7set': Attach('emergency close of all shutters', Moveable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
        'timeout': Override(mandatory=False, default=5),
    }

    positions = ['close', 'S1', 'S2', 'S3']
    valuetype = oneof(*positions)

    def doIsAllowed(self, pos):
        # only shutter close is allowed
        if pos != 'close':
            return False, 'can only close shutter from remote'
        return True, ''

    def doStart(self, target):
        if target == self.read(0):
            return
        self._attached_sr7set.start(self.positions.index(target))
        if self.wait() != target:
            raise PositionError(self, 'device returned wrong position')
        self.log.info('SR7: %s', target)

    def doRead(self, maxage=0):
        res = self.doStatus()[0]
        if res == status.OK:
            if self._attached_sr7cl.read(maxage) == 1:
                return 'close'
            elif self._attached_sr7p1.read(maxage) == 1:
                return 'S1'
            elif self._attached_sr7p2.read(maxage) == 1:
                return 'S2'
            elif self._attached_sr7p3.read(maxage) == 1:
                return 'S3'
        else:
            raise PositionError(self, 'SR7 shutter moving or undefined')

    def doStatus(self, maxage=0):
        cl, p1, p2, p3 = self._attached_sr7cl.read(maxage), \
            self._attached_sr7p1.read(maxage), self._attached_sr7p2.read(maxage), \
            self._attached_sr7p3.read(maxage)
        if p1 == 1 and p2 == 1 and p3 == 1:
            return status.BUSY, 'moving'
        elif cl == 1 or p1 == 1 or p2 == 1 or p3 == 1:
            return status.OK, 'idle'
        else:
            return status.ERROR, 'undefined position'
