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
#
# *****************************************************************************

"""PUMA multianalyzer coupled 'att' axis."""

import math

from nicos import session
from nicos.core import Attach, HasLimits, HasPrecision, Moveable, Override, \
    Param, floatrange, status
from nicos.core.errors import PositionError
from nicos.core.utils import filterExceptions, multiReset, multiStatus


class CoupledAxis(HasPrecision, HasLimits, Moveable):
    """PUMA multianalyzer coupled 'att' axis.

    This axis moves two axes and the movement of one axis is allowed only
    in a limited range in correlation to the current position of the other
    axis.

    At the moment the method is written especially for the analyser 2 theta
    movement, if the multianalyser is on PUMA and does not use a threaded
    movement.
    """

    hardware_access = False

    attached_devices = {
        'tt': Attach('tth', Moveable),
        'th': Attach('th', Moveable),
    }

    parameter_overrides = {
        # 'timeout': Override(settable=False, default=600),
        'precision': Override(settable=False, default=.1),
        'abslimits': Override(mandatory=False, default=(-60, 0)),
    }

    parameters = {
        'difflimit': Param('increment of the allowed angle movement of one '
                           'axis without collision of the other axis',
                           type=floatrange(0, 60), settable=False, default=3.),
        'dragerror': Param('Maximum deviation between both axes when read out '
                           'during a positioning step', unit='main', default=1,
                           settable=True),
        '_status': Param('read only status',
                         type=bool, settable=False, internal=True,
                         default=False),
    }

    @property
    def tt(self):
        """Return the attached 'tt' device."""
        return self._attached_tt

    @property
    def th(self):
        """Return the attached 'th' device."""
        return self._attached_th

    def doInit(self, mode):
        """Init device."""
        # maximum angle difference allowed for the two axes before movement
        # or initialization
        try:
            self.__setDiffLimit()
        except PositionError:
            pass
        self._setROParam('_status', False)

    def doIsAllowed(self, target):
        """Check whether position given by target is allowed."""
        tt_allowed = self.tt.isAllowed(target)
        th_allowed = self.th.isAllowed(-target)
        if tt_allowed[0] and th_allowed[0]:
            if self._checkZero(self.tt.read(0), self.th.read(0)):
                return True, ''
            return False, '%s and %s are not close enough' % (self.tt, self.th)
        return False, '; '.join([th_allowed[1], tt_allowed[1]])

    def doStart(self, target):
        """Move coupled axis (tt/th).

        The tt axis should without moving the coupled axis th (tt + th == 0)
        """
        if self.doStatus(0)[0] == status.BUSY:
            self.log.error('device busy')

        position = (target, -target)
        if not self._checkReachedPosition(position):
            try:
                self._setROParam('_status', True)

                self.__setDiffLimit()

                tt = self.tt.read(0)
                th = self.th.read(0)

                if abs(tt - position[0]) > self.difflimit or \
                   abs(th - position[1]) > self.difflimit:
                    delta = abs(tt - target)
                    mod = math.fmod(delta, self.difflimit)
                    steps = int(delta / self.difflimit)
                    self.log.debug('delta/self.difflimit, mod: %s, %s', steps,
                                   mod)

                    if tt > target:
                        self.log.debug('case tt > position')
                        delta = -self.difflimit
                    elif tt < target:
                        self.log.debug('case tt < position')
                        delta = self.difflimit

                    for i in range(1, steps + 1):
                        d = i * delta
                        self.log.debug('step: %d, move tt: %.2f, th: %.2f:',
                                       i, tt + d, th - d)
                        self.__setDiffLimit()
                        self.th.move(th - d)
                        self.tt.move(tt + d)
                        self._hw_wait()
                else:
                    steps = 1

                if not self._checkReachedPosition(position):
                    self.log.debug('step: %d, move tt: %.2f, th: %.2f:',
                                   steps, target, -target)
                    self.__setDiffLimit()
                    self.th.move(-target)
                    self.tt.move(target)
                    self._hw_wait()
                if not self._checkReachedPosition(position):
                    PositionError(self, "couldn't reach requested position "
                                  '%7.3f' % target)
            finally:
                self.log.debug('Clear status flag')
                self._setROParam('_status', False)
                self.poll()

    def _hw_wait(self):

        loops = 0
        final_exc = None
        devlist = [self.tt, self.th]
        while devlist:
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.doStatus(0)[0]
                except Exception as exc:
                    dev.log.exception('while waiting')
                    final_exc = filterExceptions(exc, final_exc)
                    # remove this device from the waiters - we might still
                    # have its subdevices in the list so that _hw_wait()
                    # should not return until everything is either OK or
                    # ERROR
                    devlist.remove(dev)
                if done == status.BUSY:
                    # we found one busy dev, normally go to next iteration
                    # until this one is done (saves going through the whole
                    # list of devices and doing unnecessary HW communication)
                    if loops % 10:
                        break
                    # every 10 loops, go through everything to get an accurate
                    # display in the action line
                    continue
                devlist.remove(dev)
            if devlist:
                session.delay(self._base_loop_delay)
        if final_exc:
            raise final_exc

    def doReset(self):
        """Reset individual axes, set angle between axes within one degree."""
        multiReset([self.tt, self.th])
        tt, th = self.tt.read(0), self.th.read(0)

        if not self._checkZero(tt, th):
            if (tt + th) <= self.difflimit:
                self.tt.maw(-th)
                return
            raise PositionError(self, '%s and %s are not close enough' %
                                (self.tt, self.th))

    def doRead(self, maxage=0):
        """Read back the value of the 2theta axis."""
        tt, _ = self.tt.read(maxage), self.th.read(maxage)
        return tt

    def doStatus(self, maxage=0):
        """Return status of device in dependence of the individual axes."""
        if self._status:
            return status.BUSY, 'moving'
        return multiStatus(self._adevs, maxage)

    def __setDiffLimit(self):
        """Set limits of device in dependence of allowed set of difflimit."""
        if self._checkZero(self.tt.read(0), self.th.read(0)):
            for ax in [self.tt, self.th]:
                p = ax.read(0)
                self.log.debug('%s, %s', ax, p)
                limit = self.difflimit
                absMin = p - (limit + 2. * ax.precision - 0.0001)
                absMax = p + (limit + 2. * ax.precision - 0.0001)
                self.log.debug('user limits for %s: %r',
                               ax.name, (absMin, absMax))
                # ax.userlimits = (absMin, absMax)
                self.log.debug('user limits for %s: %r', ax.name,
                               ax.userlimits)
        else:
            raise PositionError(self, 'cannot set new limits; coupled axes %s '
                                'and %s are not close enough difference > %f '
                                'deg.' % (self.tt, self.th, self.difflimit))

    def _checkReachedPosition(self, pos):
        """Check if requested positions are reached for individual axes."""
        if pos is None:
            return False
        # This may appear in the test and fresh setup systems
        if None in (self.tt.target, self.th.target):
            return False
        return (self.tt.isAtTarget(target=pos[0])
                and self.th.isAtTarget(target=pos[1]))

    def _checkZero(self, tt, th):
        """Check if the two axes are within the allowed limit."""
        return abs(tt + th) <= self.dragerror
