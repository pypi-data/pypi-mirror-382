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
#   Michael Wedel <michael.wedel@esss.se>
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import threading

from nicos.core import Moveable, Override, Param, oneof, pvname, status
from nicos.core.errors import ConfigurationError
from nicos.core.mixins import CanDisable, HasLimits, HasOffset
from nicos.devices.abstract import CanReference, Motor
from nicos.devices.epics.pva.epics_devices import EpicsMoveable


class EpicsMotor(CanDisable, CanReference, HasOffset, EpicsMoveable, Motor):
    """
    This device exposes some of the functionality provided by the EPICS motor
    record. The PV names for the fields of the record (readback, speed, etc.)
    are derived by combining the motorpv-parameter with the predefined field
    names.

    The has_errorbit and has_reseterror can be provided optionally in case the
    controller supports reporting errors and a reset-mechanism that tries to
    recover from certain errors. If present, these are used when calling the
    reset()-method.

    Another optional parameter is the has_errormsg, which contains an error message that
    may originate from the motor controller or the IOC. If it is present,
    doStatus uses it for some of the status messages.
    """
    valuetype = float

    parameters = {
        'motorpv':
            Param('Name of the motor record PV.',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
        'has_powerauto':
            Param('Optional PV for auto enable power.',
                  type=bool,
                  default=True,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'has_errormsg':
            Param('Optional PV with error message.',
                  type=bool,
                  default=True,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'has_errorbit':
            Param('Optional PV with error bit.',
                  type=bool,
                  default=True,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'has_reseterror':
            Param('Optional PV with error reset switch.',
                  type=bool,
                  default=True,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'reference_direction':
            Param('Reference run direction.',
                  type=oneof('forward', 'reverse'),
                  default='forward',
                  settable=False,
                  userparam=False,
                  mandatory=False),
        'position_deadband':
            Param('Acceptable distance between target and final position.',
                  type=float,
                  settable=False,
                  volatile=True,
                  userparam=False,
                  mandatory=False),
        'pv_desc':
            Param('The description defined at the EPICS level.',
                  type=str,
                  settable=False,
                  volatile=True,
                  userparam=False,
                  mandatory=False),
    }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),

        # speed, limits and offset may change from outside, can't rely on cache
        'speed': Override(volatile=True),
        'offset': Override(volatile=True, chatty=False),
        'abslimits': Override(volatile=True, mandatory=False),

        # Units are set by EPICS, so cannot be changed
        'unit': Override(mandatory=False, settable=False, volatile=True),
    }

    _motor_status = (status.OK, '')

    # Fields of the motor record for which an interaction via Channel Access
    # is required.
    _record_fields = {
        'readpv': 'RBV',
        'writepv': 'VAL',
        'stop': 'STOP',
        'donemoving': 'DMOV',
        'moving': 'MOVN',
        'miss': 'MISS',
        'homeforward': 'HOMF',
        'homereverse': 'HOMR',
        'speed': 'VELO',
        'offset': 'OFF',
        'highlimit': 'HLM',
        'lowlimit': 'LLM',
        'softlimit': 'LVIO',
        'lowlimitswitch': 'LLS',
        'highlimitswitch': 'HLS',
        'enable': 'CNEN',
        'set': 'SET',
        'foff': 'FOFF',
        'units': 'EGU',
        'alarm_status': 'STAT',
        'alarm_severity': 'SEVR',
        'position_deadband': 'RDBD',
        'description': 'DESC',
    }

    _suffixes = {
        'powerauto': '-PwrAuto',
        'errormsg': '-MsgTxt',
        'errorbit': '-Err',
        'reseterror': '-ErrRst',
    }

    _cache_relations = {
        'readpv': 'value',
        'units': 'unit',
        'writepv': 'target',
    }

    def doInit(self, mode):
        self._lock = threading.Lock()
        EpicsMoveable.doInit(self, mode)

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in motor record.

        :return: List of PV aliases.
        """
        pvs = set(self._record_fields.keys())

        for suffix in self._suffixes:
            if getattr(self, 'has_' + suffix):
                pvs.add(suffix)

        return pvs

    def _get_status_parameters(self):
        status_pars = {
            'miss',
            'donemoving',
            'moving',
            'lowlimitswitch',
            'highlimitswitch',
            'softlimit',
            'alarm_status',
            'alarm_severity',
        }

        if self.has_errormsg:
            status_pars.add('errormsg')
        return status_pars

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the motorpv parameter.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        motor_record_prefix = getattr(self, 'motorpv')
        motor_field = self._record_fields.get(pvparam)

        if motor_field is not None:
            return '.'.join((motor_record_prefix, motor_field))

        motor_suffix = self._suffixes.get(pvparam)

        if motor_suffix is not None:
            return ''.join((motor_record_prefix, motor_suffix))

        return getattr(self, pvparam)

    def doReadSpeed(self):
        return self._get_pv('speed')

    def doWriteSpeed(self, value):
        speed = self._get_valid_speed(value)

        if speed != value:
            self.log.warning(
                'Selected speed %s is outside the parameter '
                'limits, using %s instead.', value, speed)

        self._put_pv('speed', speed)

    def doReadOffset(self):
        return self._get_pv('offset')

    def doWriteOffset(self, value):
        # In EPICS, the offset is defined in following way:
        # USERval = HARDval + offset
        if self.offset != value:
            diff = value - self.offset

            # Set the offset in motor record
            self._put_pv_blocking('offset', value)

            # Read the absolute limits from the device as they have changed.
            self.abslimits  # pylint: disable=pointless-statement

            # Adjust user limits into allowed range
            usmin = max(self.userlimits[0] + diff, self.abslimits[0])
            usmax = min(self.userlimits[1] + diff, self.abslimits[1])
            self.userlimits = (usmin, usmax)

            self.log.info('The new user limits are: %s', self.userlimits)

    def doAdjust(self, oldvalue, newvalue):
        # For EPICS the offset sign convention differs to that of the base
        # implementation.
        diff = oldvalue - newvalue
        self.offset -= diff

    def _get_valid_speed(self, newValue):
        min_speed, max_speed = self._get_speed_limits()
        valid_speed = newValue
        if min_speed != 0.0:
            valid_speed = max(min_speed, valid_speed)

        if max_speed != 0.0:
            valid_speed = min(max_speed, valid_speed)

        return valid_speed

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doStart(self, value):
        self._put_pv('writepv', value)

    def doReadTarget(self):
        return self._get_pv('writepv')

    def doStatus(self, maxage=0):
        with self._lock:
            epics_status, message = self._get_alarm_status()
            self._motor_status = epics_status, message
        if epics_status == status.ERROR:
            return status.ERROR, message or 'Unknown problem in record'
        elif epics_status == status.WARN:
            return status.WARN, message

        done_moving = self._get_pv('donemoving')
        moving = self._get_pv('moving')
        if done_moving == 0 or moving != 0:
            if self._get_pv('homeforward') or self._get_pv('homereverse'):
                return status.BUSY, message or 'homing'
            return status.BUSY, message or f'moving to {self.target}'

        if self.has_powerauto:
            powerauto_enabled = self._get_pv('powerauto')
        else:
            powerauto_enabled = 0

        if not powerauto_enabled and not self._get_pv('enable'):
            return status.WARN, 'motor is not enabled'

        miss = self._get_pv('miss')
        if miss != 0:
            return (status.NOTREACHED, message
                    or 'did not reach target position.')

        high_limitswitch = self._get_pv('highlimitswitch')
        if high_limitswitch != 0:
            return status.WARN, message or 'at high limit switch.'

        low_limitswitch = self._get_pv('lowlimitswitch')
        if low_limitswitch != 0:
            return status.WARN, message or 'at low limit switch.'

        limit_violation = self._get_pv('softlimit')
        if limit_violation != 0:
            return status.WARN, message or 'soft limit violation.'

        return status.OK, message

    def _get_alarm_status(self):
        stat, msg = self.get_alarm_status('readpv')
        if self.has_errormsg:
            err_msg = self._get_pv('errormsg', as_string=True)
            if stat == status.UNKNOWN:
                stat = status.ERROR
            if self._motor_status != (stat, err_msg):
                self._log_epics_msg_info(err_msg, stat, msg)
            return stat, err_msg
        return stat, msg

    def _log_epics_msg_info(self, error_msg, stat, epics_msg):
        if stat in (status.OK, status.UNKNOWN):
            return
        if stat == status.WARN:
            self.log.warning('%s (%s)', error_msg, epics_msg)
        elif stat == status.ERROR:
            self.log.error('%s (%s)', error_msg, epics_msg)

    def _get_speed_limits(self):
        return self._get_limits('speed')

    def doStop(self):
        self._put_pv('stop', 1, False)

    def _checkLimits(self, limits):
        # Called by doReadUserlimits and doWriteUserlimits
        low, high = self.abslimits
        if low == 0 and high == 0:
            # No limits defined in IOC.
            # Could be a rotation stage for example.
            return

        if limits[0] < low or limits[1] > high:
            raise ConfigurationError('cannot set user limits outside of '
                                     'absolute limits (%s, %s)' % (low, high))

    def doReadAbslimits(self):
        absmin = self._get_pv('lowlimit')
        absmax = self._get_pv('highlimit')
        return absmin, absmax

    def doReset(self):
        if self.has_errorbit and self.has_reseterror:
            error_bit = self._get_pv('errorbit')
            if error_bit == 0:
                self.log.warning(
                    'Error bit is not set, can not reset error state.')
            else:
                self._put_pv('reseterror', 1)

    def doReference(self):
        self._put_pv('home%s' % self.reference_direction, 1)

    def doEnable(self, on):
        what = 1 if on else 0
        self._put_pv('enable', what, False)

    def doSetPosition(self, pos):
        self._put_pv('set', 1)
        self._put_pv('foff', 1)
        self._put_pv('writepv', pos)
        self._put_pv('set', 0)
        self._put_pv('foff', 0)

    def isAtTarget(self, pos=None, target=None):
        return self._get_pv('miss') == 0

    def doReadUnit(self):
        return self._get_pv('units')

    def _check_in_range(self, curval, userlimits):
        if userlimits == (0, 0) and self.abslimits == (0, 0):
            # No limits defined, so must be in range
            return status.OK, ''

        return HasLimits._check_in_range(self, curval, userlimits)

    def doReadPosition_Deadband(self):
        return self._get_pv('position_deadband')

    def doReadPv_Desc(self):
        return self._get_pv('description')

    def isAllowed(self, pos):
        if self.userlimits == (0, 0) and self.abslimits == (0, 0):
            # No limits defined
            return True, ''

        return Moveable.isAllowed(self, pos)
