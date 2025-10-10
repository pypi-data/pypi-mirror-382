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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************
"""Classes for the focussing guide."""

from nicos.core import Attach, Moveable, Override, oneof


class BeamFocus(Moveable):

    attached_devices = {
        'ellipse': Attach('output signal for ellipse', Moveable),
        'collimator': Attach('output signal for collimator', Moveable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
        'fmtstr': Override(default='%s'),
    }

    valuetype = oneof('Ell', 'Col')

    hardware_access = False

    def doInit(self, mode):
        ell_state = self._attached_ellipse.read(0)
        col_state = self._attached_collimator.read(0)
        if [ell_state, col_state] == [1, 1]:
            self.reset()

    def doReset(self):
        self._attached_ellipse.move(0)
        self._attached_collimator.move(0)

    def doStart(self, target):
        if not self.isAtTarget(target=target):
            devs = [self._attached_ellipse, self._attached_collimator]
            pos = [1, 0] if target == 'Ell' else [0, 1]
            for d, p in zip(devs, pos):
                d.maw(p)
            self._hw_wait()

    def isAtTarget(self, pos=None, target=None):
        if target is None:
            target = self.target
        if pos is None:
            pos = self.doRead(0)
        return pos == target

    def doRead(self, maxage=0):
        ell = self._attached_ellipse.read(maxage)
        col = self._attached_collimator.read(maxage)
        if [ell, col] == [0, 1]:
            return 'Col'
        elif [ell, col] == [1, 0]:
            return 'Ell'
        return None
