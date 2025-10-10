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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

import json
from time import time as currenttime

from streaming_data_types.status_x5f2 import deserialise_x5f2
from streaming_data_types.utils import get_schema

from nicos import session
from nicos.core import MASTER, POLLER, Override, Param, Readable, status, \
    tupleof
from nicos.core.constants import SIMULATION

from nicos_ess.devices.kafka.consumer import KafkaSubscriber

DISCONNECTED_STATE = (status.ERROR, 'Disconnected')


class KafkaStatusHandler(KafkaSubscriber, Readable):
    """ Communicates with Kafka and receives status updates.
    The communicator also allows to communicate the status messages
    via callback providing new status messages and their timestamps.
    """

    parameters = {
        'statustopic':
            Param(
                'Kafka topic where status messages are written',
                type=str,
                settable=False,
                preinit=True,
                mandatory=True,
                userparam=False,
            ),
        'timeoutinterval':
            Param(
                'Time to wait (secs) before communication is considered lost',
                type=int,
                default=5,
                settable=True,
                userparam=False,
            ),
        'curstatus':
            Param(
                'Store the current device status',
                internal=True,
                type=tupleof(int, str),
                settable=True,
            ),
        'statusinterval':
            Param(
                'Expected time (secs) interval for the status message updates',
                type=int,
                default=2,
                settable=True,
                internal=True,
            ),
    }

    _next_update = 0

    parameter_overrides = {
        'unit': Override(mandatory=False, userparam=False),
    }

    def doPreinit(self, mode):
        KafkaSubscriber.doPreinit(self, mode)
        if session.sessiontype != POLLER and mode != SIMULATION:
            self.subscribe(self.statustopic)

        # Be pessimistic and assume the process is down, if the process
        # is up then the status will be remedied quickly.
        self._next_update = currenttime()

        if self._mode == MASTER:
            self._setROParam('curstatus',
                             (status.WARN, 'Trying to connect...'))

    def doRead(self, maxage=0):
        return ''

    def doStatus(self, maxage=0):
        return self.curstatus

    def new_messages_callback(self, messages):
        json_messages = {}
        for timestamp, message in messages:
            try:
                if get_schema(message) != 'x5f2':
                    continue
                msg = deserialise_x5f2(message)
                js = json.loads(msg.status_json) if msg.status_json else {}
                js['update_interval'] = msg.update_interval
                json_messages[timestamp] = js
                self._set_next_update(msg.update_interval)
            except Exception as e:
                self.log.warning(
                    'Could not decode message from status topic: %s', e)

        if json_messages:
            self._status_update_callback(json_messages)

    def no_messages_callback(self):
        # Check if the process is still running
        if self._mode == MASTER and not self.is_process_running():
            self._setROParam('curstatus', DISCONNECTED_STATE)

    def is_process_running(self):
        # Allow some leeway in case of message lag.
        if currenttime() > self._next_update + self.timeoutinterval:
            return False
        return True

    def _status_update_callback(self, messages):
        """This method is called whenever a new status messages appear on
        the status topic. The subclasses should define this method if
        a callback is required when new status messages appear.
        :param messages: dict of timestamp and message in JSON format
        """

    def _set_next_update(self, update_interval):
        update_interval = update_interval // 1000
        if self.statusinterval != update_interval:
            self._setROParam('statusinterval', update_interval)
        next_update = currenttime() + self.statusinterval
        self._next_update = max(self._next_update, next_update)
