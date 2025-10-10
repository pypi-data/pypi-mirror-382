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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

"""Sans1 spin flipper specific commands."""

from nicos import session
from nicos.commands import helparglist, hiddenusercommand
from nicos.commands.scan import scan
from nicos.core import UsageError


@hiddenusercommand
@helparglist('counting_time, flipper_value')
def polcount(time, value=30):
    """
    Performs a count for preset time [s] with spin up and spin down.
    """
    try:
        time = float(time)
        value = float(value)
    except ValueError:
        raise UsageError('both counting time and flipper value '
                         'should be numbers!') from None
    scan(session.getDevice('P_spinflipper'), [value, 0], time=time)
