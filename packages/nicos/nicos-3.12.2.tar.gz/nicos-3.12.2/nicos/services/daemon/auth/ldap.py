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
#
# *****************************************************************************

import re

import ldap3  # pylint: disable=import-error

from nicos.core import ACCESS_LEVELS, Param, User, dictof, listof, oneof
from nicos.core.params import string
from nicos.services.daemon.auth import AuthenticationError, \
    Authenticator as BaseAuthenticator

# do not use default repr, which might leak passwords
ldap3.Connection.__repr__ = object.__repr__

ldapuri_re = re.compile(
    r'^((ldaps|ldap)://)?[a-z0-9-]+(\.[a-z0-9-]+)*(:[1-9][0-9]*)?(/)?$', re.I)


def ldapuri(val=None):
    """a valid LDAP URI with just the host part like [ldap[s]://]host[:port]"""
    if val in ('', None):
        return ''
    val = string(val)
    if not ldapuri_re.match(val):
        raise ValueError('%r is not a valid LDAP URI' % val)
    return val


FORBIDDEN = -1


class Authenticator(BaseAuthenticator):
    """Authenticates against the configured LDAP server.

    Basically it tries to bind on the server with the given userdn.
    Per default, all ldap users are rejected when there is no user level
    definition inside the 'roles' dictionary.
    """

    BIND_METHODS = {
        'none': ldap3.AUTO_BIND_NONE,
        'no_tls': ldap3.AUTO_BIND_NO_TLS,
        'tls_before_bind': ldap3.AUTO_BIND_TLS_BEFORE_BIND,
        'tls_after_bind': ldap3.AUTO_BIND_TLS_AFTER_BIND,
    }

    parameters = {
        'uri':         Param('LDAP connection URIs',
                             type=listof(ldapuri), mandatory=True),
        'bindmethod':  Param('LDAP port', type=oneof(*BIND_METHODS),
                             default='no_tls'),
        'userbasedn':  Param('Base dn to query users.',
                             type=str,
                             mandatory=True),
        'userfilter':  Param('Filter for querying users. Must contain '
                             '"%(username)s"', type=str,
                             default='(&(uid=%(username)s)'
                             '(objectClass=posixAccount))'),
        'groupbasedn': Param('Base dn to query groups',
                             type=str,
                             mandatory=True),
        'groupfilter': Param('Filter for querying groups. '
                             'Must contain "%(gidnumber)s"', type=str,
                             default='(&(gidNumber=%(gidnumber)s)'
                             '(objectClass=posixGroup))'),
        'usergroupfilter': Param('Filter groups of a specific user. '
                                 'Must contain "%(username)s"', type=str,
                                 default='(&(memberUid=%(username)s)'
                                 '(objectClass=posixGroup))'),
        'userroles':   Param('Dictionary of allowed users with their '
                             'associated role',
                             type=dictof(str, oneof(*ACCESS_LEVELS.values()))),
        'grouproles':  Param('Dictionary of allowed groups with their '
                             'associated role',
                             type=dictof(str, oneof(*ACCESS_LEVELS.values()))),
    }

    def doInit(self, mode):
        self._access_levels = {value: key
                               for key, value in ACCESS_LEVELS.items()}

    def authenticate(self, username, password):
        userdn = self._get_user_dn(username)

        # first of all: try a bind to check user existence and password
        error = None
        try:
            connection = ldap3.Connection(self.uri, user=userdn,
                                          password=password,
                                          auto_bind=self.BIND_METHODS[
                                              self.bindmethod])
        except ldap3.core.exceptions.LDAPException as err:
            # this avoids leaking credential details via tracebacks
            error = str(err)
        if error:
            raise AuthenticationError('LDAP connection failed (%s)' % error)

        userlevel = FORBIDDEN
        # check if the user has explicit rights
        if username in self.userroles:
            userlevel = self._access_levels[self.userroles[username]]
            return User(username, userlevel)

        # if no explicit user right was given, check group rights
        groups = self._get_user_groups(connection, username)

        for group in groups:
            if group in self.grouproles:
                userlevel = max(userlevel,
                                self._access_levels[self.grouproles[group]])

        if userlevel != FORBIDDEN:
            return User(username, userlevel)

        raise AuthenticationError('Login not permitted for the given user')

    def _get_user_groups(self, connection, username):
        # start with the users default group
        groups = [self._get_default_group(connection, username)]

        # find additional groups of the user
        filter_str = self.usergroupfilter % {'username': username}
        connection.search(self.groupbasedn, filter_str, ldap3.LEVEL,
                          attributes=ldap3.ALL_ATTRIBUTES)

        for group in connection.response:
            groups.append(group['attributes']['cn'][0])

        return groups

    def _get_default_group(self, connection, username):
        filter_str = self.userfilter % {'username': username}

        if not connection.search(self.userbasedn, filter_str, ldap3.LEVEL,
                                 attributes=ldap3.ALL_ATTRIBUTES):
            raise AuthenticationError('User not found in LDAP directory')

        return self._get_group_name(
            connection,
            connection.response[0]['attributes']['gidNumber'])

    def _get_group_name(self, connection, gid):
        filter_str = self.groupfilter % {'gidnumber': gid}
        if not connection.search(self.groupbasedn, filter_str, ldap3.LEVEL,
                                 attributes=ldap3.ALL_ATTRIBUTES):
            raise AuthenticationError('Group %s not found' % gid)
        return connection.response[0]['attributes']['cn'][0]

    def _get_user_dn(self, username):
        return 'uid=%s,%s' % (username, self.userbasedn)
