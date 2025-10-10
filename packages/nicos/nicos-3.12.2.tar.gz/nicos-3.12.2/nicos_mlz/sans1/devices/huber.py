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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special device for Huber absolute encoded axis"""


from nicos.core import HasOffset
from nicos.devices.entangle import Actuator


class HuberAxis(HasOffset, Actuator):

    def doRead(self, maxage=0):
        return Actuator.doRead(self, maxage) - self.offset

    def doStart(self, target):
        return Actuator.doStart(self, target + self.offset)

    def doAdjust(self, oldvalue, newvalue):
        return HasOffset.doAdjust(self, oldvalue, newvalue)

    def doSetPosition(self, pos):
        # just adjust the offset, do not interact with HW!
        self.doAdjust(self.read(0), pos)
