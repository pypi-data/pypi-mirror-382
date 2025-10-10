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

import numpy as np

from nicos.core import Attach, Override, Param, Readable, status


class Wavelength(Readable):
    """Return the DNS wavelength as given by the ton position."""

    attached_devices = {
        'angle': Attach('Ton angle', Readable),
    }

    parameters = {
        'dvalue': Param('Monochromator d-value', default=3.355),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='A'),
    }

    def doRead(self, maxage=0):
        angle = self._attached_angle.read(maxage) / 180 * np.pi
        return np.sin(angle / 2) * 2 * self.dvalue

    def doStatus(self, maxage=0):
        return status.OK, ''
