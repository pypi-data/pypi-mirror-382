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

"""Helpers for the "instrument config" dialog."""

import os

from nicos import config
from nicos.utils import safeWriteFile


def _get_instr_config():
    currentfile = os.path.join(config.setup_package_path, config.instrument,
                               'setups', 'current_%s.py' % config.instrument)
    with open(currentfile, encoding='utf-8') as fp:
        return fp.read()


def _apply_instr_config(code):
    currentfile = os.path.join(config.setup_package_path, config.instrument,
                               'setups', 'current_%s.py' % config.instrument)
    safeWriteFile(currentfile, code, maxbackups=0)
