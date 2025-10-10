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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from scipy.interpolate import interp1d

from nicos.core import Device, IsController
from nicos.core.device import Moveable
from nicos.core.params import Attach, Param, listof


class EIS2TController(IsController, Device):
    """
    This controller keeps track of EI and S2T and tries to stop users from
    running CAMEA into the wall
    """

    attached_devices = {
        'ei': Attach('Incident energy device', Moveable),
        's2t': Attach('Detector two theta', Moveable),
    }

    parameters = {
        'ei_values': Param('List of EI values', type=listof(float)),
        's2t_values': Param('S2T limit for each ei in ei_Values',
                            type=listof(float)),
    }

    def doInit(self, mode):
        self._interpolate_s2t = interp1d(self.ei_values, self.s2t_values)

    def isAdevTargetAllowed(self, adev, adevtarget):
        if adev == self._attached_ei:
            s2t_limit = self._interpolate_s2t(adevtarget)
            if self._attached_s2t.read(0) <= s2t_limit:
                return False, 'You are running the detector into the wall'
        else:
            s2t_limit = self._interpolate_s2t(self._attached_ei.read(0))
            if adevtarget <= s2t_limit:
                return False, 'You are running the detector into the wall'
        return True, ''
