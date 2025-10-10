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

name = 'test_alias setup'

includes = ['stdsystem', 'slit']

devices = dict(
    v1 = device('nicos.devices.generic.VirtualMotor',
        abslimits = (0, 5),
        unit = 'mm',
        speed = 1.5,
    ),
    aliasNoDev = device('nicos.devices.generic.DeviceAlias',
        alias = '',
        devclass = 'nicos.core.device.Readable',
    ),
    aliasDev = device('nicos.devices.generic.DeviceAlias',
        alias = '',
        devclass = 'nicos.devices.generic.VirtualMotor',
    ),
    aliasDev2 = device('nicos.devices.generic.DeviceAlias',
        alias = 'slit',
    ),
    aliasDev3 = device('nicos.devices.generic.DeviceAlias',
        alias = '',
    ),
    aliasDev4 = device('nicos.devices.generic.DeviceAlias',
        alias = '',
        devclass = 'nicos.devices.generic.VirtualMotor',
    ),
    axis_motor = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
        userlimits = (-50, 50),
    ),
    axis = device('nicos.devices.generic.Axis',
        motor = 'axis_motor',
        coder = 'axis_motor',
        obs = [],
        precision = 0,
    ),
)
