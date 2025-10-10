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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS PANDA Experiment."""

from os import path

from nicos.core import Override, Param
from nicos.core.params import host, none_or

from nicos_mlz.devices.experiment import Experiment


class PandaExperiment(Experiment):
    parameter_overrides = {
        'templates':     Override(default='exp/template'),
        'servicescript': Override(default='start_service.py'),
    }

    parameters = {
        'ariane_host': Param('Host for connection to ARIANE runtime',
                             type=none_or(host(defaultport=11657)),
                             default=None),
    }

    @property
    def proposalsymlink(self):
        """deviating from default of <dataroot>/current"""
        return path.join(self.dataroot, 'currentexperiment')
