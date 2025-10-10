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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS triple-axis instrument devices."""

from math import asin, cos, degrees, pi, radians, sin

from nicos.core import MASTER, SIMULATION, Attach, HasLimits, HasPrecision, \
    LimitError, Moveable, Override, Param, listof, multiReset, multiStatus, \
    oneof, status, tupleof
from nicos.devices.generic.mono import ANG2MEV, THZ2MEV, \
    Monochromator as BaseMonochromator, from_k, to_k


def wavevector(dvalue, order, theta):
    return pi * order / (dvalue * sin(radians(theta)))


def thetaangle(dvalue, order, k):
    return degrees(asin(pi * order / (k * dvalue)))


class Monochromator(HasLimits, HasPrecision, BaseMonochromator):
    """General monochromator theta/two-theta device.

    It supports setting the `unit` parameter to different values and will
    calculate the theta/two-theta angles correctly for each supported value:

    * "A-1" -- wavevector in inverse Angstrom
    * "A" -- wavelength in Angstrom
    * "meV" -- energy in meV
    * "THz" -- energy in THz

    Also supported is a focussing monochromator setup.  For this, set the
    `focush` and `focusv` attached devices to the axes that control the
    focussing, and set `hfocuspars` and `vfocuspars` to a list of coefficients
    (starting with the constant coefficient) for a polynomial that calculates
    the `focush` and `focusv` values from a given wavelength.
    """

    attached_devices = {
        'theta':    Attach('Monochromator rocking angle', HasPrecision),
        'twotheta': Attach('Monochromator scattering angle', HasPrecision),
        'focush':   Attach('Horizontal focusing axis', Moveable,
                           optional=True),
        'focusv':   Attach('Vertical focusing axis', Moveable,
                           optional=True),
    }

    hardware_access = False

    parameters = {
        'dvalue':   Param('d-value of the reflection used', unit='A',
                          mandatory=True, settable=True,
                          category='instrument'),
        'mosaic':   Param('Mosaicity of the crystal',
                          unit='deg', default=0.5,
                          settable=True, category='instrument'),
        'order':    Param('Order of reflection to use', type=int, default=1,
                          settable=True, category='instrument'),
        'reltheta': Param('True if theta position is relative to two-theta',
                          type=bool, default=False, category='instrument'),
        'focmode':  Param('Focussing mode', default='manual', settable=True,
                          type=oneof('manual', 'flat', 'horizontal',
                                     'vertical', 'double'),
                          category='instrument'),
        'hfocuspars': Param('Horizontal focus polynomial coefficients',
                            type=listof(float), default=[0.], settable=True,
                            category='instrument'),
        'hfocusflat': Param('Horizontal focus value for flat mono',
                            type=float, default=0, settable=True),
        'vfocuspars': Param('Vertical focus polynomial coefficients',
                            type=listof(float), default=[0.], settable=True,
                            category='instrument'),
        'vfocusflat': Param('Vertical focus value for flat mono',
                            type=float, default=0, settable=True),
        'scatteringsense': Param('Scattering sense', type=oneof(1, -1),
                                 chatty=True, userparam=False,
                                 settable=True, category='instrument'),
        'crystalside': Param('Scattering sense for which theta is two-theta/2 '
                             '(for the other sense it needs to be offset by '
                             '180 degrees to avoid scattering from the back '
                             'of the crystal holder)',
                             type=oneof(1, -1), mandatory=True),
        'material': Param('Crystal material',
                          type=oneof('PG', 'Ge', 'Si', 'Cu', 'Fe3Si',  'CoFe',
                                     'Heusler', 'Diamond', 'Multilayer'),
                          mandatory=True, category='instrument'),
        'reflection': Param('Used hkl parameter of the reflection',
                            type=tupleof(int, int, int), mandatory=True,
                            category='instrument'),
    }

    parameter_overrides = {
        'precision': Override(volatile=True, settable=False),
    }

    def doInit(self, mode):
        # warnings about manual focus
        self._focwarnings = 3

        # need to consider rounding effects since a difference of 0.0104 is
        # rounded to 0.010 so the combined axisprecision need to be larger than
        # the calculated value the following correction seems to work just fine
        self._axisprecision = self._attached_twotheta.precision + \
            2 * self._attached_theta.precision
        self._axisprecision *= 1.25

    def doReset(self):
        multiReset(list(self._adevs.values()))
        self._focwarnings = 3

    def _calc_angles(self, k):
        try:
            angle = thetaangle(self.dvalue, self.order, k)
        except ValueError:
            raise LimitError(
                self, 'wavelength not reachable with d=%.3f A and n=%s' % (
                    self.dvalue, self.order)) from None
        tt = 2.0 * angle * self.scatteringsense  # twotheta with correct sign
        th = angle * self.scatteringsense  # absolute theta with correct sign
        th = (angle - 90.0) * self.scatteringsense + 90.0 * self.crystalside
        # correct for theta axis mounted on top of two-theta table
        if self.reltheta:
            th -= tt
        return th, tt

    def doStart(self, target):
        th, tt = self._calc_angles(to_k(target, self.unit))
        self._attached_twotheta.start(tt)
        self._attached_theta.start(th)
        self._movefoci(self.focmode, self.hfocuspars, self.vfocuspars)
        self._sim_setValue(target)

    def _movefoci(self, focmode, hfocuspars, vfocuspars):
        # get goalposition in A
        target = self.target
        if target is None:
            target = self.doRead(0)
        lam = from_k(to_k(target, self.unit), 'A')
        focusv, focush = self._attached_focusv, self._attached_focush
        if focmode == 'flat':
            if focusv:
                focusv.move(self.vfocusflat)
            if focush:
                focush.move(self.hfocusflat)
        elif focmode == 'horizontal':
            if focusv:
                focusv.move(self.vfocusflat)
            if focush:
                focush.move(self._calfocus(lam, hfocuspars))
        elif focmode == 'vertical':
            if focusv:
                focusv.move(self._calfocus(lam, vfocuspars))
            if focush:
                focush.move(self.hfocusflat)
        elif focmode == 'double':
            if focusv:
                focusv.move(self._calfocus(lam, vfocuspars))
            if focush:
                focush.move(self._calfocus(lam, hfocuspars))
        else:
            if self._focwarnings and (focusv or focush):
                self.log.warning('focus is in manual mode')
                self._focwarnings -= 1

    def _calfocus(self, lam, focuspars):
        temp = lam * float(self.order)
        focus = 0
        for i, coeff in enumerate(focuspars):
            focus += coeff * (temp**i)
        return focus

    def doIsAllowed(self, pos):
        try:
            theta = thetaangle(self.dvalue, self.order, to_k(pos, self.unit))
        except ValueError:
            return False, 'wavelength not reachable with d=%.3f A and n=%s' % \
                (self.dvalue, self.order)
        ttvalue = 2.0 * self.scatteringsense * theta
        ttdev = self._attached_twotheta
        ok, why = ttdev.isAllowed(ttvalue)
        if not ok:
            return ok, '[%s] moving to %s, ' % (
                ttdev, ttdev.format(ttvalue, unit=True)) + why
        return True, ''

    def _get_angles(self, maxage):
        tt = self._attached_twotheta.read(maxage)
        th = self._attached_theta.read(maxage)
        if self.reltheta:
            th += tt
        th = (th - 90.0 * self.crystalside) * self.scatteringsense + 90.0
        return tt * self.scatteringsense, th

    def doRead(self, maxage=0):
        # the scattering angle is deciding
        tt = self.scatteringsense * self._attached_twotheta.read(maxage)
        if tt == 0.0:
            return 0.0
        return from_k(wavevector(self.dvalue, self.order, tt/2.0), self.unit)

    def doStatus(self, maxage=0):
        # order is important here.
        const, text = multiStatus(((name, self._adevs[name]) for name in
                                   ['theta', 'twotheta', 'focush', 'focusv']),
                                  maxage)
        if const == status.OK:  # all idle; check also angle relation
            tt, th = self._get_angles(maxage)
            if abs(tt - 2.0*th) > self._axisprecision:
                return status.NOTREACHED, \
                    'two theta and 2*theta axis mismatch: %s <-> %s = 2 * %s'\
                    % (tt, 2.0*th, th)
        return const, text

    def doFinish(self):
        tt, th = self._get_angles(0)
        if abs(tt - 2.0*th) > self._axisprecision:
            self.log.warning('two theta and 2*theta axis mismatch: %s <-> '
                             '%s = 2 * %s', tt, 2.0*th, th)
            self.log.info('precisions: tt:%s, th:%s, combined: %s',
                          self._attached_twotheta.precision,
                          self._attached_theta.precision, self._axisprecision)

    def doReadPrecision(self):
        if not hasattr(self, 'scatteringsense'):
            # object not yet intialized
            return 0
        # the precision depends on the angular precision of theta and twotheta
        val = self.read()
        if val == 0.0:
            return 0.0
        lam = from_k(to_k(val, self.unit), 'A')
        dtheta = self._attached_theta.precision + \
            self._attached_twotheta.precision
        dlambda = abs(2.0 * self.dvalue *
                      cos(self._attached_twotheta.read() * pi/360) *
                      dtheta / 180*pi)
        if self.unit == 'A-1':
            return 2*pi/lam**2 * dlambda
        elif self.unit == 'meV':
            return 2*ANG2MEV / lam**3 * dlambda
        elif self.unit == 'THz':
            return 2*ANG2MEV / THZ2MEV / lam**3 * dlambda
        return dlambda

    def doWriteFocmode(self, value):
        if value != 'manual':
            self.log.info('moving foci to new values')
        self._movefoci(value, self.hfocuspars, self.vfocuspars)

    def doWriteHfocuspars(self, value):
        self.log.info('moving foci to new values')
        self._movefoci(self.focmode, value, self.vfocuspars)

    def doWriteVfocuspars(self, value):
        self.log.info('moving foci to new values')
        self._movefoci(self.focmode, self.hfocuspars, value)

    def doUpdateUnit(self, value):
        if 'unit' not in self._params:
            # this is the initial update
            return
        if self._mode not in (MASTER, SIMULATION):
            # change limits only from the master copy, or in simulation mode
            return
        new_absmin = from_k(to_k(self.abslimits[0], self.unit), value)
        new_absmax = from_k(to_k(self.abslimits[1], self.unit), value)
        if new_absmin > new_absmax:
            new_absmin, new_absmax = new_absmax, new_absmin
        self._setROParam('abslimits', (new_absmin, new_absmax))
        if self.userlimits != (0, 0):
            new_umin = from_k(to_k(self.userlimits[0], self.unit), value)
            new_umax = from_k(to_k(self.userlimits[1], self.unit), value)
            if new_umin > new_umax:
                new_umin, new_umax = new_umax, new_umin
            new_umin = max(new_umin, new_absmin)
            new_umax = min(new_umax, new_absmax)
            self.userlimits = (new_umin, new_umax)
        if 'target' in self._params and self.target and \
                self.target != 'unknown':
            # this should be still within the limits
            self._setROParam(
                'target', from_k(to_k(self.target, self.unit), value))
        self.read(0)

    def _calcurvature(self, l1, l2, k, vertical=True):
        """Calculate optimum curvature (1/radius) for given lengths and
        monochromator rotation angle (given by wavevector in A-1).
        """
        theta = thetaangle(self.dvalue, self.order, k)
        exp = vertical and -1 or +1
        return 0.5*(1./l1 + 1./l2)*sin(radians(abs(theta)))**exp

    def _adjust(self, newvalue, unit):
        """Adjust the offsets of theta and twotheta to let the device value
        match the given value.
        """
        th, tt = self._calc_angles(to_k(newvalue, unit))
        thdiff = self._attached_theta.read(0) - th
        ttdiff = self._attached_twotheta.read(0) - tt
        self._attached_theta.offset += thdiff
        self._attached_twotheta.offset += ttdiff
