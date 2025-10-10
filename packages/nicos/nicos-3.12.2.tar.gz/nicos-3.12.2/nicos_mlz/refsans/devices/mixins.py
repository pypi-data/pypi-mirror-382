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
#
# **************************************************************************
"""Support Code for REFSANS's NOK's."""

import numpy as np

from nicos.core import DeviceMixinBase
from nicos.core.params import Param, floatrange, nonemptylistof


class PseudoNOK(DeviceMixinBase):
    """Placeholder device, doing nothing, but storing some locational data."""

    parameters = {
        'nok_start': Param('Start of the  NOK (beginning from NLE2b)',
                           type=floatrange(-1), settable=False,
                           mandatory=False, unit='mm', default=-1),
        'nok_end':   Param('End of the NOK (beginning from NLE2b)',
                           type=floatrange(-1), default=-1, settable=False,
                           mandatory=False, unit='mm'),
        'nok_gap':   Param('Gap after the NOK (beginning from NLE2b)',
                           type=floatrange(0), default=0, settable=False,
                           mandatory=False, unit='mm'),
        'masks':     Param('Masks for this NOK',
                           type=dict, settable=False, default={}),
        'length':    Param('NOK length',
                           type=floatrange(0), settable=False,
                           mandatory=False, volatile=True, unit='mm'),
    }

    def doReadLength(self):
        return self.nok_end - self.nok_start


class PolynomFit(DeviceMixinBase):
    """Fit values to a polynom."""

    parameters = {
        'poly': Param('Polynomial coefficients in ascending order for '
                      'potentiometer calibration',
                      type=nonemptylistof(float), settable=False,
                      mandatory=False, default=[0., 1.]),
    }

    _fitter = np.polynomial.Polynomial([0., 1.])  # identity conversion

    def doUpdatePoly(self, poly):
        self._fitter = np.polynomial.Polynomial(poly)

    def _fit(self, value):
        self.log.debug('uncorrected value: %f', value)
        result = self._fitter(value)
        self.log.debug('fitted result: %f', result)
        return result
