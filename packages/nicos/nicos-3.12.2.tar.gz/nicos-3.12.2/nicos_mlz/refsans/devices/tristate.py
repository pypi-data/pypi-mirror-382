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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************

from nicos.core import Readable, status
from nicos.core.mixins import CanDisable, HasOffset
from nicos.core.params import Attach


class TriState(CanDisable, HasOffset, Readable):
    attached_devices = {
        'port': Attach('port to read the real number', Readable),
    }

    _enabled = True

    hardware_access = False

    def doRead(self, maxage=0):
        self.log.debug('enabled=%s', self._enabled)
        if self._enabled:
            self.log.debug('offset=%.3f', self.offset)
            return self._attached_port.read(maxage) - self.offset
        return 0

    def doStatus(self, maxage=0):
        if self._enabled:
            stat = self._attached_port.status(maxage)
            if stat[0] == status.OK:
                return status.OK, 'enabled'
            return stat
        return status.DISABLED, 'disabled'

    def doEnable(self, on):
        self._enabled = on
