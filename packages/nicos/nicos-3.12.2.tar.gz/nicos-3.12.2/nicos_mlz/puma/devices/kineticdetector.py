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

"""Special devices for kinetic measurements."""

from nicos.devices.generic.detector import ActiveChannel, Detector


class KineticDetector(Detector):
    """Special detector for kinetic measurements.

    If the monitor names don't start with 'mon' the original names will be used
    as preset keys.
    """

    def _presetiter(self):
        """yields name, device tuples for all 'preset-able' devices"""
        # a device may react to more than one presetkey....
        for i, dev in enumerate(self._attached_timers):
            if isinstance(dev, ActiveChannel):
                if i == 0:
                    yield ('t', dev, 'time')
                    yield ('time', dev, 'time')
                yield ('timer%d' % (i + 1), dev, 'time')
        for i, dev in enumerate(self._attached_monitors):
            if isinstance(dev, ActiveChannel):
                if dev.name.lower().startswith('mon'):
                    yield ('mon%d' % (i + 1), dev, 'monitor')
                else:
                    yield (dev.name.lower(), dev, 'monitor')
        for i, dev in enumerate(self._attached_counters):
            if isinstance(dev, ActiveChannel):
                if i == 0:
                    yield ('n', dev)
                yield ('det%d' % (i + 1), dev, 'counts')
                yield ('ctr%d' % (i + 1), dev, 'counts')
        for i, dev in enumerate(self._attached_images):
            if isinstance(dev, ActiveChannel):
                yield ('img%d' % (i + 1), dev, 'counts')
        yield ('live', None, 'other')
