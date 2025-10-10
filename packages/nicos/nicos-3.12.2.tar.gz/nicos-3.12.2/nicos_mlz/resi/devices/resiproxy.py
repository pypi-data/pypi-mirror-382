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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Created on 30.05.2011

@author: pedersen
"""

import sys

from nicos.utils.proxy import NicosProxy

sys.path.append('/home/pedersen/Eclispe_projects_git/singlecounter')
sys.path.append('/usr/local/nonius_new/app')
# pylint: disable=import-error
from goniometer.position import PositionFromStorage  # isort:skip



class ResiPositionProxy(NicosProxy):
    """
    proxy class to make  position objects really picklable

    """
    __hardware = None

    @classmethod
    def SetHardware(cls,hw):
        ResiPositionProxy.__hardware = hw

    def __getstate__(self):
        return self._obj.storable()
    def __setstate__(self,state):
        self._obj = PositionFromStorage(ResiPositionProxy.__hardware, state)
