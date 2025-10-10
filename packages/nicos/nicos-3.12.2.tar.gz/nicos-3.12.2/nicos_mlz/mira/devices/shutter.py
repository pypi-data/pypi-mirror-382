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

"""Class for MIRA shutter readout/operation."""

from nicos import session
from nicos.core import SIMULATION, SLAVE, ModeError, Param, Readable, status, \
    usermethod
from nicos.devices.tango import PyTangoDevice


class Shutter(PyTangoDevice, Readable):
    """
    Class for readout of the MIRA shutter via digital input card, and closing
    the shutter via digital output (tied into Pilz security system).
    """

    valuetype = str

    parameters = {
        'openoffset':   Param('The bit offset for the "shutter open" input',
                              type=int, mandatory=True),
        'closeoffset':  Param('The bit offset for the "shutter closed" input',
                              type=int, mandatory=True),
        'switchoffset': Param('The bit offset for the "close shutter" output',
                              type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._dev.WriteOutputWord([0x1120, 0])

    def doStatus(self, maxage=0):
        is_open = self._dev.ReadInputBit(self.openoffset)
        is_clsd = self._dev.ReadInputBit(self.closeoffset)
        if is_open + is_clsd == 1:
            return status.OK, ''
        return status.BUSY, 'moving'

    def doRead(self, maxage=0):
        is_open = self._dev.ReadInputBit(self.openoffset)
        is_clsd = self._dev.ReadInputBit(self.closeoffset)
        if is_open and not is_clsd:
            return 'open'
        elif is_clsd and not is_open:
            return 'closed'
        return ''

    @usermethod
    def close(self):
        """Closes instrument shutter."""
        if self._mode == SLAVE:
            raise ModeError(self, 'closing shutter not allowed in slave mode')
        elif self._sim_intercept:
            return
        self._dev.WriteOutputBit([self.switchoffset, 1])
        session.delay(0.5)
        self._dev.WriteOutputBit([self.switchoffset, 0])
        self.log.info('instrument shutter closed')
