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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Status code definitions."""

# The status constants are ordered by ascending "severity": this way the status
# constant for a combined device is very easily determined as the maximum of
# the subordinate device values.
OK = 200
WARN = 210
BUSY = 220
NOTREACHED = 230
DISABLED = 235
ERROR = 240
UNKNOWN = 999

# dictionary mapping all status constants to their names
statuses = {v: k.lower() for (k, v) in globals().items() if isinstance(v, int)}
