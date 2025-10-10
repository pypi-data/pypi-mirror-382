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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS TOFTOF experiment class."""

from nicos import session
from nicos.core.params import Override

from nicos_mlz.devices.experiment import Experiment as BaseExperiment


class Experiment(BaseExperiment):
    """TOFTOF experiment.

    The service experiment will be filled up with instrument specific data.
    """

    parameter_overrides = {
        'envlist': Override(category='general'),
    }

    def _newPropertiesHook(self, proposal, kwds):
        if self.proptype == 'service':
            upd = {
                'title': 'Maintenance',
                'users': [{'name': session.instrument.responsible}],
                'localcontacts': [{'name': session.instrument.responsible}],
                'default_sample': 'Unknown',
            }
            kwds.update(upd)
            return kwds
        return BaseExperiment._newPropertiesHook(self, proposal, kwds)
