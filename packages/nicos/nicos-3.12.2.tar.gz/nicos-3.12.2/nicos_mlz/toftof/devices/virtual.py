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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""Virtual devices for testing."""

import numpy as np

from nicos.core import Override, Param, intrange
from nicos.devices.generic.virtual import VirtualImage as BaseImage

from nicos_mlz.toftof.lib import calculations as calc


class VirtualImage(BaseImage):
    """Virtual 2-dimensional detector that generates TOFTOF data.

    The data will be generated from real measured data weighted by time.
    """

    parameters = {
        'datafile': Param('File to load the pixel data',
                          settable=False, type=str,
                          default='nicos_mlz/toftof/data/test/data.npz',
                          ),
        'timechannels': Param('Number of time channels per detector channel',
                              type=intrange(1, 4096), settable=True,
                              default=1024,
                              ),
        'frametime': Param('Time interval between pulses',
                           type=float, settable=True, default=0.1,
                           ),
        'delay': Param('TOF frame delay',
                       type=int, settable=True,
                       ),
        'timeinterval': Param('duration of a single time slot',
                              volatile=True,
                              ),
        'numinputs': Param('Number of detector channels',
                           type=intrange(1, 1024), settable=True, default=1024,
                           ),
        'monitorchannel': Param('Channel number of the monitor counter',
                                type=intrange(1, 1024), settable=True,
                                default=956,
                                ),
    }

    parameter_overrides = {
        'size': Override(default=(1024, 1024), prefercache=False),
    }

    _rawdata = None

    def doInit(self, mode):
        BaseImage.doInit(self, mode)
        try:
            with open(self.datafile, 'rb') as fp:
                self._rawdata = 0.01 * np.load(fp).reshape(self.size)
            self.log.warning('%r', self._rawdata.shape)
            # eliminate monitor entries
            self._rawdata[self.monitorchannel] = np.zeros(
                self._rawdata.shape[1])
        except OSError:
            self.log.warning('data file %s not present, returning empty array '
                             'from virtual TOF image', self.datafile)
            self._rawdata = np.zeros(self.size)

    def _generate(self, t):
        return np.random.poisson(t * self._rawdata)

    def doReadTimeinterval(self):
        return 5e-8 * int(1.0 + self.frametime / (calc.ttr * 1024))
