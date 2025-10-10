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

"""Class for KWS selector."""

from nicos.core import Attach, Moveable, Param, dictof, dictwith
from nicos.devices.entangle import WindowTimeoutAO
from nicos.devices.generic.switcher import MultiSwitcher

from nicos_mlz.kws1.devices.detector import DetectorPosSwitcherMixin


class SelectorSpeed(WindowTimeoutAO):
    """
    Control selector speed.
    """

    def doTime(self, old_value, target):
        return abs(target - old_value) / 110.0


class SelectorLambda(Moveable):
    """
    Control selector wavelength directly, converting between speed and
    wavelength.

    This uses not the default conversion from the Astrium selector classes,
    since the selector is tilted against the beam, and it is easier to use
    the constant determined by wavelength calibration.
    """

    parameters = {
        'constant': Param('Conversion constant: '
                          'lam[Ang] = constant/speed[Hz] + offset',
                          mandatory=True, unit='Ang Hz'),
        'offset':   Param('Conversion offset: '
                          'lam[Ang] = constant/speed[Hz] + offset',
                          default=0, unit='Ang'),
    }

    attached_devices = {
        'seldev': Attach('The selector speed device', Moveable),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        speed = self._attached_seldev.read(maxage)
        return (60 * self.constant / speed) + self.offset if speed else -1

    def doIsAllowed(self, value):
        if value == 0:
            return False, 'zero wavelength not allowed'
        speed = int(round(60 * self.constant / (value - self.offset)))
        return self._attached_seldev.isAllowed(speed)

    def doStart(self, target):
        speed = int(round(60 * self.constant / (target - self.offset)))
        self.log.debug('moving selector to %f rpm', speed)
        self._attached_seldev.start(speed)


class SelectorSwitcher(MultiSwitcher):
    """Switcher whose mapping is determined by a list of presets."""

    parameters = {
        'presets':  Param('Presets that determine the mapping',
                          type=dictof(str, dictwith(lam=float, speed=float,
                                                    spread=float)),
                          mandatory=True),
    }

    attached_devices = {
        'det_pos':  Attach('Detector preset device', DetectorPosSwitcherMixin),
    }

    def doUpdateValue(self, position):
        self._attached_det_pos._updateMapping(position)

    def _getWaiters(self):
        return self._attached_moveables

    def _start_unchecked(self, pos):
        MultiSwitcher._start_unchecked(self, pos)
        self._attached_det_pos._updateMapping(pos)
