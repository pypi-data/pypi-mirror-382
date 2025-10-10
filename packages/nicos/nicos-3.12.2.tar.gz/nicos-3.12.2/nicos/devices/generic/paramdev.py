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

"""Generic device class for "moving" a parameter of another device."""

from nicos.core import Attach, Device, Moveable, Override, Param, Readable, \
    status


class ReadonlyParamDevice(Readable):
    """
    A pseudo-device that returns the value of the parameter on read().
    """

    hardware_access = False

    attached_devices = {
        'device':  Attach('The device to control the selected parameter',
                          Device),
    }

    parameters = {
        'parameter': Param('The name of the parameter to use', type=str,
                           mandatory=True),
        'copy_status': Param('Derive status from the master device', type=bool,
                             mandatory=False, settable=True, chatty=True,
                             default=False),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    def _getWaiters(self):
        if self.copy_status:
            return [self._attached_device]
        return []

    def doRead(self, maxage=0):
        return getattr(self._attached_device, self.parameter)

    def doStatus(self, maxage=0):
        if self.copy_status:
            return self._attached_device.status(maxage)
        return status.OK, ''

    def doReadUnit(self):
        devunit = getattr(self._attached_device, 'unit', '')
        parunit = self._attached_device._getParamConfig(
            self.parameter).unit or ''
        if devunit:
            parunit = parunit.replace('main', devunit)
        return parunit


class ParamDevice(ReadonlyParamDevice, Moveable):
    """
    A pseudo-device that sets the value of a selected parameter of another
    device on start(), and returns the value of the parameter on read().
    """

    def doInit(self, mode):
        self.valuetype = self._attached_device._getParamConfig(
            self.parameter).type

    def doStart(self, target):
        setattr(self._attached_device, self.parameter, target)
