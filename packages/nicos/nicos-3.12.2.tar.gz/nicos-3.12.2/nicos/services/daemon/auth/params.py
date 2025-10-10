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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import ACCESS_LEVELS


def _access_level_list():
    return ', '.join(repr(l) for l in ACCESS_LEVELS.values())


def UserPassLevelAuthEntry(val=None):
    """Provide a 3-tuple of user, password, and level

        * user: string
        * password: string
        * level: oneof(ACCESS_LEVELS)
           currently: GUEST, USER, ADMIN
    """
    val = list(val)
    if len(val) != 3:
        raise ValueError('UserPassLevelAuthEntry entry needs to be '
                         'a 3-tuple (name, password, accesslevel)')
    if not isinstance(val[0], str):
        raise ValueError('user name must be a string')
    val[0] = val[0].strip()
    if not isinstance(val[1], str):
        raise ValueError('user password must be a string')
    val[1] = val[1].strip()
    if isinstance(val[2], str):
        for i, name in ACCESS_LEVELS.items():
            if name == val[2].strip():
                val[2] = i
                break
        else:
            raise ValueError('access level must be one of %s' % _access_level_list())
    elif not isinstance(val[2], int):
        # for backwards compatibility: allow integer values as well
        raise ValueError('access level must be one of %s' % _access_level_list())
    else:
        if val[2] not in ACCESS_LEVELS:
            raise ValueError('access level must be one of %s' % _access_level_list())
    return tuple(val)


def UserLevelAuthEntry(val=None):
    """Provide a 2-tuple of user and level

        * user: string
        * level: oneof(ACCESS_LEVELS)
           currently: GUEST, USER, ADMIN
    """
    if len(val) != 2:
        raise ValueError('UserLevelAuthEntry entry needs to be a 2-tuple '
                         '(name, accesslevel)')
    # pylint: disable=unbalanced-tuple-unpacking
    user, _p, level = UserPassLevelAuthEntry((val[0], '', val[1]))
    return tuple((user, level))
