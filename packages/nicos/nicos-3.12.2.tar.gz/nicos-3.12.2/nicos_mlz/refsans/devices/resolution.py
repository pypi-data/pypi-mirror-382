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

"""Devices to display some instrument values in status monitor."""

from nicos.core import Override, Readable
from nicos.core.params import Attach

from nicos_mlz.refsans.lib.calculations import chopper_resolution, \
    pre_sample_path


class Resolution(Readable):
    """Calculate the wavelength resolution of the whole instrument.

    The chopper controller device is used to detect the real and virtual
    position of the second disc (chopper2).
    """
    attached_devices = {
        'chopper': Attach('chopper controller device', Readable),
        'flightpath': Attach('Read the real flightpath', Readable),
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        return chopper_resolution(
            self._attached_chopper.read(maxage).get('chopper2_pos', 5),
            self._attached_flightpath.read(maxage))

    def doReadUnit(self):
        return '%'


class RealFlightPath(Readable):

    attached_devices = {
        'table': Attach('port to read real table', Readable),
        'pivot': Attach('port to read real pivot', Readable),
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        table = self._attached_table.read(maxage)
        pivot = self._attached_pivot.read(maxage)
        self.log.debug('table=%s, pivot=%s', table, pivot)
        # in meter
        D = (table + pivot * self._attached_pivot.grid + pre_sample_path) / 1e3
        self.log.debug('D=%.2f %s', D, self.unit)
        return D

    def doReadUnit(self):
        return 'm'
