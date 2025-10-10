# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2017-2025 by the NICOS contributors (see AUTHORS)
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
#   Bjoern Pedersen <bjoern.pedersen@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""
Calculate Sample illumination for reflectometers
"""

from numpy import nan, radians, sin

from nicos.core import Attach, Param, Readable
from nicos.devices.generic import Slit


class SampleIllumination(Readable):


    parameters = {
        's1pos': Param('Slit 1 position relative to sample',
                       mandatory=True, type=float),
        's2pos': Param('Slit 2 position relative to sample',
                       mandatory=True, type=float),
        'f0':    Param('Footprint for n * pi, 0 <= n <= N',
                       type=float, default=nan)
    }
    attached_devices = {
        's1':    Attach('First slit', Slit),
        's2':    Attach('Second slit', Slit),
        'theta': Attach('Incidence angle', Readable)
    }

    def doRead(self, maxage=0):
        """Calculate the beam footprint (illumination on the sample)."""
        # l1= distance between slits
        l1 = self.s1pos - self.s2pos
        # l2 distance from last slit to sample
        l2 = self.s2pos
        # get slit width
        s1w = self._attached_s1.width.read(maxage)
        s2w = self._attached_s2.width.read(maxage)
        theta = self._attached_theta.read(maxage)

        denominator = abs(sin(radians(theta)))
        if denominator < 1e-4:
            return self.f0
        return (min(s1w, s2w) + l2 / l1 * (s1w + s2w)) / denominator
