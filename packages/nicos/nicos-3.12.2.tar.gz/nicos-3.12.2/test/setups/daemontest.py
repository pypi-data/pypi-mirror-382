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

name = 'test_axis setup'

includes = ['stdsystem']

devices = dict(
    dm1 = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
        userlimits = (-50, 50),
    ),
    dmalias = device('nicos.devices.generic.DeviceAlias',
        alias = 'dm1',
    ),
    dax = device('nicos.devices.generic.Axis',
        motor = 'dm1',
        coder = None,
        obs = [],
        precision = 0,
        loopdelay = 0.02,
        loglevel = 'debug',
    ),
    dm2 = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
    ),
)

help_topics = dict(
    nicos_demo = '''
This entry examples description of something very specific to nicos_demo.
Since it is actually what is currently loaded.
''',
    RST = '''
#. List entry **1**.
''',
)
