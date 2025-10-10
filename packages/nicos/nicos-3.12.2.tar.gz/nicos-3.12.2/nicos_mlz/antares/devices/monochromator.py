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
# *****************************************************************************

"""Antares Monochromator"""

from math import asin, degrees, radians, sin, tan

from nicos.core import Attach, HasLimits, Moveable, NicosError, Override, \
    Param, PositionError, anytype, dictof, floatrange, none_or, oneof, \
    status
from nicos.core.utils import multiStatus, statusString
from nicos.utils import lazy_property


class Monochromator(HasLimits, Moveable):
    """Monochromator device of antares.

    Used to tune the double monochromator to a wavelength between 1.4 and 6.0
    Angstroms.  Can be moved to None to get a white beam.

    Experimental version.
    CHECK THE FORMULAS!
    """
    attached_devices = {
        'phi1':        Attach('monochromator rotation 1', Moveable),
        'phi2':        Attach('monochromator rotation 2', Moveable),
        'translation': Attach('monochromator translation', Moveable),
        'inout':       Attach('monochromator inout device', Moveable),
    }

    parameters = {
        'dvalue1':    Param('Lattice constant of Mono1', type=float,
                            settable=True, mandatory=True),
        'dvalue2':    Param('Lattice constant of Mono2', type=float,
                            settable=True, mandatory=True),
        'distance':   Param('Parallactic distance of monos', type=float,
                            settable=True, mandatory=True),
        'tolphi':     Param('Max deviation of phi1 or phi2 from calculated '
                            'value',
                            type=float, settable=True, default=0.01),
        'toltrans':   Param('Max deviation of translation from calculated '
                            'value',
                            type=float, settable=True, default=0.01),
        'parkingpos': Param('Monochromator parking position',
                            type=dictof(oneof(*attached_devices.keys()),
                                        anytype),
                            mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='Angstrom'),
    }

    valuetype = none_or(floatrange(1.4, 6.0))

    hardware_access = False

    @lazy_property
    def devices(self):
        return [self._adevs[i] for i in 'inout phi1 phi2 translation'.split()]

    def _from_lambda(self, lam):
        """Return 3 values used for phi1, phi2 and translation."""
        phi1 = degrees(asin(lam / float(2 * self.dvalue1)))
        phi2 = degrees(asin(lam / float(2 * self.dvalue2)))
        trans = self.distance / tan(2 * radians(phi1))
        return phi1, phi2, trans

    def _to_lambda(self, phi1, phi2, trans):
        """Calculate lambda from phi1, phi2, trans. May raise a PositionError.
        Not necessarily all arguments are used.

        Next iteration could evaluate all 3 args and return an average value...
        """
        try:
            return abs(2 * self.dvalue1 * sin(radians(phi1)))
        except Exception:
            raise PositionError('can not determine lambda!') from None

    def _moveToParkingpos(self):
        for dev, target in self.parkingpos.items():
            self._adevs[dev].start(target)

    def doStart(self, target):
        if target is None:
            self.log.debug('None given; Moving to parking position')
            self._moveToParkingpos()
            return

        if self._attached_inout.read() == 'out':
            self.log.debug('moving monochromator into beam')

        for d, v in zip(self.devices, ['in'] + list(self._from_lambda(target))):
            self.log.debug('sending %s to %r', d.name, v)
            d.start(v)

    def doStatus(self, maxage=0):
        st = multiStatus(list(self._adevs.items()), maxage)
        if st[0] == status.OK:
            # check position
            try:
                self.doRead(maxage)
            except PositionError as e:
                return status.NOTREACHED, str(e)
        return st

    def _combinedStatus(self, maxage=0):
        try:
            stvalue = self.doStatus(maxage)
        except NicosError as err:
            stvalue = (status.ERROR, str(err))
        except Exception as err:
            stvalue = (status.ERROR, 'unhandled %s: %s' %
                       (err.__class__.__name__, err))
        if stvalue[0] not in status.statuses:
            stvalue = (status.UNKNOWN,
                       'status constant %r is unknown' % stvalue[0])

        if stvalue[0] == status.OK:
            value = self.read(maxage)
            if value is None:  # parking pos
                return stvalue
            wl = self.warnlimits
            if wl:
                if wl[0] is not None and value < wl[0]:
                    stvalue = status.WARN, \
                        statusString(stvalue[1], 'below warn limit (%s)' %
                                     self.format(wl[0], unit=True))
                elif wl[1] is not None and value > wl[1]:
                    stvalue = status.WARN, \
                        statusString(stvalue[1], 'above warn limit (%s)' %
                                     self.format(wl[1], unit=True))
        return stvalue

    def doRead(self, maxage=0):
        pos = [d.read(maxage) for d in self.devices]

        # Are we in the beam?
        if pos[0] == 'out':
            return None

        # calculate lambda from phi1 and then check the other positions
        # for consistency...
        lam = self._to_lambda(*pos[1:])
        self.log.debug('lambda seems to be %.4f Angstroms', lam)
        compare_pos = self._from_lambda(lam)
        tol = [self.tolphi, self.tolphi, self.toltrans]
        for d, p, t, c in zip(self.devices[1:], pos[1:], tol, compare_pos):
            self.log.debug('%s is at %s and should be at %s for %.4f '
                           'Angstroms', d, d.format(p), d.format(c), lam)
            if abs(p - c) > t:
                raise PositionError('%s is too far away for %.4f Angstroms' %
                                    (d, lam))
        return lam
