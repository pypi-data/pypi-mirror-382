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

"""Devices for the Beckhoff Busklemmensystem."""

from nicos.core import SIMULATION, Param, listof
from nicos.devices import entangle


class DigitalInput(entangle.DigitalInput):
    """Device object for a 1-bit digital input device via a Beckhoff modbus
    interface.
    """

    valuetype = int

    parameters = {
        'offset': Param('Offset of digital input',
                        type=int, mandatory=True),
    }

    def doRead(self, maxage=0):
        return self._dev.ReadInputBit(self.offset)


class NamedDigitalInput(entangle.NamedDigitalInput):
    """Device object for a 1-bit digital input device via a Beckhoff modbus
    interface.
    """

    valuetype = int

    parameters = {
        'offset': Param('Offset of digital input',
                        type=int, mandatory=True),
    }

    def doRead(self, maxage=0):
        value = self._dev.ReadInputBit(self.offset)
        return self._reverse.get(value, value)


class DigitalOutput(entangle.DigitalOutput):
    """Device object for a digital output device via a Beckhoff modbus
    interface.
    """

    valuetype = listof(int)

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
        'bitwidth':    Param('Number of bits to switch', type=int,
                             mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._dev.WriteOutputWord([0x1120, 0])

    def doRead(self, maxage=0):
        return tuple(self._dev.ReadOutputBits([self.startoffset,
                                               self.bitwidth]))

    def doStart(self, target):
        self._dev.WriteOutputBits([self.startoffset] + target)

    def doIsAllowed(self, target):
        try:
            if len(target) != self.bitwidth:
                return False, ('value needs to be a sequence of length %d, '
                               'not %r' % (self.bitwidth, target))
        except TypeError:
            return False, 'invalid value for device: %r' % target
        return True, ''

    def doReadFmtstr(self):
        return '[' + ', '.join(['%s'] * self.bitwidth) + ']'


class NamedDigitalOutput(entangle.NamedDigitalOutput):
    """Device object for a digital output device via a Beckhoff modbus
    interface.
    """

    parameters = {
        'startoffset': Param('Starting offset of digital output values',
                             type=int, mandatory=True),
    }

    def doInit(self, mode):
        # switch off watchdog, important before doing any write access
        if mode != SIMULATION:
            self._dev.WriteOutputWord([0x1120, 0])
        entangle.NamedDigitalOutput.doInit(self, mode)

    def doStart(self, target):
        value = self._forward.get(target, target)
        self._dev.WriteOutputBit([self.startoffset, value])

    def doRead(self, maxage=0):
        value = self._dev.ReadOutputBit(self.startoffset)
        return self._reverse.get(value, value)
