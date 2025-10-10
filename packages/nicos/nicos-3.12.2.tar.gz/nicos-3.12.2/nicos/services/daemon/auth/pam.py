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
#
# *****************************************************************************

import pwd
import re

import pamela as pam

from nicos.core import ADMIN, GUEST, USER, Param, User, oneof
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator

access_re = re.compile(r'access=(?P<level>\d+)')


class Authenticator(BaseAuthenticator):
    """Authenticates against PAM.

    This unfortunately only works against the local shadow database if the
    daemon runs as the root user.

    The access level info can be put into the "gecos" field.

    Example:

    John Doe,access=20

    where 20 is the 'ADMIN' level. (see `nicos.core.utils.py` file)
    """

    parameters = {
        'defaultlevel': Param('Default user level if not in PAM settings',
                              settable=False, userparam=False,
                              type=oneof(GUEST, USER, ADMIN), default=GUEST),
    }

    def authenticate(self, username, password):
        try:
            pam.authenticate(username, password, resetcred=0)
            entry = pwd.getpwnam(username)
            idx = access_re.search(entry.pw_gecos)
            if idx:
                access = int(idx.group('level'))
                if access in (GUEST, USER, ADMIN):
                    return User(username, access)
            return User(username, self.defaultlevel)
        except pam.PAMError as err:
            raise AuthenticationError(
                'PAM authentication failed: %s' % err) from None
        except Exception as err:
            raise AuthenticationError(
                'exception during PAM authentication: %s' % err) from None
