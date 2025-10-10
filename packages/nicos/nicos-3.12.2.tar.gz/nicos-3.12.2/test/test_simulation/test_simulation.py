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

"""Tests for simulation mode."""

from nicos.commands.basic import sleep
from nicos.commands.scan import scan
from nicos.core import SIMULATION

session_setup = 'simscan'
session_mode = SIMULATION


def test_simmode(session):
    m = session.getDevice('motor')
    det = session.getDevice('det')
    scan(m, 0, 1, 5, 0., det, 'test scan')
    assert m._sim_min == 0
    assert m._sim_max == 4
    assert m._sim_value == 4


def test_special_behavior(session):
    oldtime = session.clock.time
    sleep(1000)   # should take no time in simulation mode, but advance clock
    newtime = session.clock.time
    assert newtime - oldtime == 1000


def test_simulated_read(session):
    m = session.getDevice('manualsim')
    assert m.read() == m.default
