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
Position base class and factory function

The position handling uses quite a lot of chaining to
keep maintenance effort low.
"""

import numpy as np

from nicos import session


def PositionFactory(ptype, **kwds):
    """ Position factory function.

        parameters:

            **ptype** -- 'k' for kappa type,
                        'e' for Euler,
                        'n' for euler with counter-clock-wise motors except phi,
                        'g' for goniometermatrix,
                        'b' for bisecting,
                        'c' for C-vector,
                        'l' for lifting counter,

                        a suffix 'r' may be used to signal angles in radians

        ptype specific parameters::

            if ptype='k': omega, kappa, phi, theta
            if ptype='e': omega, chi, phi, theta
            if ptype='n': omega, chi, phi, theta
            if ptype='b': theta, phi, chi, psi
            if ptype='c': c, psi, signtheta
            if ptype='g': theta, matrix
            if ptype='l': gamma, omega, nu, signtheta


        matrix= 3x3-matrix, c= 3-vector, angles in radians.

        Alternatively, a position object 'p' can be passed, and a copy
        will be returned.

        a
    """
    p = kwds.get('p', None)
    radians = False
    if len(ptype) > 1 and ptype[1] == 'r':
        ptype = ptype[0]
        radians = True
    if p:
        return p.__class__(p)
    elif ptype in typelist:
        return typelist[ptype](_rad=radians, **kwds)
    raise TypeError('unknown ptype specified in PositionFactory()')


class PositionBase:
    def __init__(self):
        self.log = session.log

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('log')
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.log = session.log

    def _r2d(self, val, _rad):
        if not _rad:
            if val is not None:
                return np.deg2rad(val)
            return 0.0
        return val

    def asType(self, newtype, wavelength=None):
        if newtype.lower() in typelist:
            return getattr(self, 'as%s' % newtype.upper())(wavelength)
        raise TypeError('unknown position type')


from nicos.devices.sxtal.goniometer.bisect import Bisecting  # isort:skip
from nicos.devices.sxtal.goniometer.cvector import CVector  # isort:skip
from nicos.devices.sxtal.goniometer.euler import Euler  # isort:skip
from nicos.devices.sxtal.goniometer.gmatrix import GMatrix  # isort:skip
from nicos.devices.sxtal.goniometer.kappa import Kappa  # isort:skip
from nicos.devices.sxtal.goniometer.lifting import Lifting  # isort:skip
from nicos.devices.sxtal.goniometer.neuler import NEuler  # isort:skip

typelist = {'k': Kappa,
            'e': Euler,
            'b': Bisecting,
            'c': CVector,
            'g': GMatrix,
            'n': NEuler,
            'l': Lifting,
            }
