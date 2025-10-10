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

"""JCNS lab/infrastructure specific NICOS package."""

import socket
from os import path


def determine_instrument(setup_package_path):
    """JCNS lab and infrastructure way to find the instrument."""
    try:
        hostname = socket.gethostname().split('.')
        # can't use nicos.utils.getfqdn due to import dependency
        if len(hostname) == 1:
            hostname = socket.getfqdn().split('.')
        if hostname[1] in ('fourcircle', 'galaxi', 'hermes', 'jcnsse', 'tmr'):
            instrument = hostname[1]
        elif hostname[0] in ('tr1-phys',):
            instrument = 'testrack'
        elif hostname[0].startswith('seop'):
            instrument = 'seop'
        else:
            instrument = hostname[0]
    except (ValueError, IndexError, OSError):
        pass
    else:
        # ... but only if a subdir exists for it
        if path.isdir(path.join(setup_package_path, instrument)):
            return instrument
