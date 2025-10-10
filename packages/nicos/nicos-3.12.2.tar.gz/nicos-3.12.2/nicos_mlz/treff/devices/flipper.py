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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.core.params import oneof
from nicos.devices.polarized.flipper import MezeiFlipper

UP = 'up'
DOWN = 'down'


class Flipper(MezeiFlipper):
    """MezeiFlipper subclass that has values of up/down instead of on/off."""

    valuetype = oneof(UP, DOWN)

    def doRead(self, maxage=0):
        if (abs(self._attached_corr.read(maxage)) > 0.05 or
                    abs(self._attached_flip.read(maxage)) > 0.05):
            return DOWN
        return UP

    def doStart(self, target):
        if target == DOWN:
            self._attached_flip.start(self.currents[0])
            self._attached_corr.start(self.currents[1])
        else:
            self._attached_flip.start(0)
            self._attached_corr.start(0)
