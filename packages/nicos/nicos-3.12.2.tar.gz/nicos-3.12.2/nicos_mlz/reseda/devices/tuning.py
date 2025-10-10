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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.core import Attach, ConfigurationError, InvalidValueError, \
    Moveable, Override, Param, Readable, anytype, dictof, floatrange, listof, \
    nicosdev, oneof
from nicos.core.utils import multiWait

# Storage structure of tunewave tables:
# {measmode: {wavelength: {echotime: {tunedev : value}}}}


class EchoTime(Moveable):
    """Reseda echo time device.
    Provides storage and access to tunewave tables which are used to determine
    the device setup for the particular echo time, considering the measurement
    mode and the current wavelength."""

    attached_devices = {
        'wavelength': Attach('Wavelength device', Readable),
        'dependencies': Attach('Echo time dependent devices', Readable,
                               multiple=True),
    }

    parameters = {
        'zerofirst': Param('mapping of Devices to preconfigured value to be '
                           'set before applying the echo time',
                           type=dictof(nicosdev, anytype),
                           settable=True, userparam=False, default={}),
        'stopfirst': Param('list of Devices to stop before setting a new '
                           'echotime',
                           type=listof(nicosdev),
                           settable=True, userparam=False, default=[]),
        'tables': Param('Tune wave tables',
                        type=dictof(oneof('nrse', 'mieze'), dictof(float,
                                    dictof(float, dictof(str, anytype)))),
                        settable=True, internal=True),
        'currenttable': Param('Currently used tune wave tables',
                              type=dictof(float, dictof(str, anytype)),
                              settable=False, userparam=True, internal=True,
                              volatile=True),
        'tunedevs': Param('Devices used for tuning',
                          type=listof(nicosdev), settable=False, internal=True,
                          volatile=True),
        'availtables': Param('Available tunewave tables',
                             type=dictof(str, listof(float)), settable=False,
                             internal=True, volatile=True),
        'wavelengthtolerance': Param('Wavelength tolerance for table'
                                     'determination', type=float,
                                     settable=True, default=0.1),
    }
    parameter_overrides = {
        'target': Override(category='instrument'),
    }

    valuetype = float

    def doPreinit(self, mode):
        # create an internal lookup dictionary for tunedevs ({name: dev})
        self._tunedevs = {entry.name: entry
                          for entry in self._attached_dependencies}

    def doRead(self, maxage=0):
        # read all tuning devices
        devs = {key: value.read(maxage)
                for key, value in self._tunedevs.items()}

        # find correct echotime for current device setup in currently active
        # tunewave table
        for echotime, tunedevs in self.currenttable.items():
            self.log.debug('checking if we are at echotime %s', echotime)
            success = True
            for tunedev, value in tunedevs.items():
                # XXX: horrible hack
                if tunedev.endswith('reg_amp'):
                    continue
                # fuzzy matching necessary due to maybe oscillating devices
                prec = getattr(self._tunedevs[tunedev], 'precision', 0)
                if not self._fuzzy_match(value, devs.get(tunedev, None), prec):
                    self.log.debug('-> no, because %s is at %s not %s '
                                   '(prec = %s)', tunedev,
                                   devs.get(tunedev, None), value, prec)
                    success = False
                    break
            if success:
                self.log.debug('-> YES!')
                return echotime

        # return 0 as echotime and show additional info in status string
        # if the echo time could not be determined
        return 0.0

    def doStart(self, target):
        # filter unsupported echotimes
        # find best match from table
        if not self.currenttable:
            raise ConfigurationError('There is no tunewave table loaded')
        entries = list(self.currenttable.keys())
        try:
            target = floatrange(min(entries) - 1e12, max(entries) + 1e-12)(target)
        except ValueError as err:
            raise InvalidValueError(
                f'target {target} not in range {min(entries)} - {max(entries)}') from err
        for entry in self.currenttable:
            if abs(entry - target) < 1e-3:
                value = entry
                break
        else:
            raise InvalidValueError('Given echo time not supported by current '
                                    'tunewave table (%s/%s) within %s (%s)'
                                    % (getattr(session.experiment, 'measurementmode', 'mieze'),
                                       self._attached_wavelength.read(),
                                       self.wavelengthtolerance, entries))

        # stop stopfirst devices
        for devname in self.stopfirst:
            dev = session.getDevice(devname)
            self.log.debug('stopping %s', str(dev))
            dev.stop()

        # move zerofirst devices to configured value
        self.log.debug('zeroing devices')
        wait_on = set()
        for devname, val in self.zerofirst.items():
            dev = session.getDevice(devname)
            self.log.debug('moving %s to zero', str(dev))
            dev.start(val)
            wait_on.add(dev)
        self.log.debug('waiting for devices to reach zero')
        multiWait(wait_on)
        self.log.debug('devices now at zero')

        # move all tuning devices at once without blocking
        wait_on = set()
        for tunedev, val in sorted(self.currenttable[value].items()):
            if tunedev in self.stopfirst:
                self.log.debug('skipping %s (will be set later)', tunedev)
                continue
            if tunedev in self._tunedevs:
                self.log.debug('setting %s to %s', tunedev, val)
                dev = self._tunedevs[tunedev]
                dev.start(val)
                wait_on.add(dev)
            else:
                self.log.warning('tune device %r from table not in tunedevs! '
                                 'movement to %r ignored !', tunedev, val)
        self.log.debug('waiting for devices...')
        multiWait(wait_on)
        self.log.debug('devices now at configured values')

        # activate stopfirst devices
        wait_on = set()
        for devname in self.stopfirst:
            dev = session.getDevice(devname)
            val = self.currenttable[value][devname]
            self.log.debug('moving %s to %s', devname, val)
            dev.move(val)
            wait_on.add(dev)
        self.log.debug('devices now at configured values')
        multiWait(wait_on)
        self.log.debug('all done. good luck!')

    def doReadTunedevs(self):
        return sorted(self._tunedevs)

    def doReadAvailtables(self):
        return {key: sorted(value) for key, value in self.tables.items()}

    def doReadCurrenttable(self):
        cur_wavelength = self._attached_wavelength.read()

        precision = self.wavelengthtolerance
        table = self.tables.get(getattr(session.experiment, 'measurementmode', 'mieze'), {})

        # determine current tunewave table by measurement mode and fuzzy
        # matched wavelength
        for wavelength, tunewavetable in table.items():
            if self._fuzzy_match(cur_wavelength, wavelength, precision):
                return self._validate_table(tunewavetable)

        return {}

    def getTable(self, measurement_mode, wavelength):
        """Get a specific tunewave table.

        Avoid transfering all tables for each access.
        """
        return self._validate_table(
            self.tables.get(measurement_mode, {}).get(wavelength, {}))

    def setTable(self, measurement_mode, wavelength, table):
        """Set a specific tunewave table. Avoid transfering all tables for each
        access."""

        # validate table structure and device values
        table = self._validate_table(table)

        # use ordinary dicts instead of readonlydicts to be able to change them
        tables = dict(self.tables)
        mode_table = dict(tables.setdefault(measurement_mode, {}))

        # ensure float for wavelength value due to later fuzzy matching
        mode_table[float(wavelength)] = table
        tables[measurement_mode] = mode_table

        self.tables = tables

    def deleteTable(self, measurement_mode, wavelength):
        """Delete a specific tunewave table. Avoid transfering all tables for
        each access."""

        # use ordinary dicts instead of readonlydicts to be able to change them
        tables = dict(self.tables)
        tables[measurement_mode] = dict(tables.get(measurement_mode, {}))
        del tables[measurement_mode][float(wavelength)]
        self.tables = tables

    def _fuzzy_match(self, value, setpoint, precision):
        """General fuzzy matching of values (used for float comparisons)."""
        return (setpoint - precision) <= value <= (setpoint + precision)

    def _validate_table(self, table):
        """Validates the structure of a single tunewave table and and all the
        included device values (using the valuetype of the particular device).
        """
        # Structure of a single tunewave table: {echotime: {tunedev : value}}

        result = {}
        for echotime, tunedevs in table.items():
            echotime = float(echotime)
            result[echotime] = {}
            for tunedev, value in tunedevs.items():
                try:
                    result[echotime][tunedev] = self._tunedevs[tunedev].valuetype(value)
                except KeyError:  # device not configured
                    pass

        return result
