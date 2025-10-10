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

"""NICOS daemon package."""

import sys
import threading
import time

from nicos import config, nicos_version
from nicos.core import Attach, ConfigurationError, Device, Param, host, listof
from nicos.core.utils import system_user
from nicos.protocols.daemon.classic import DEFAULT_PORT
from nicos.services.daemon.auth import Authenticator
from nicos.services.daemon.script import ExecutionController
from nicos.utils import createThread, formatExtendedStack, importString, \
    parseHostPort


class NicosDaemon(Device):
    """
    This class abstracts the main daemon process.
    """

    attached_devices = {
        'authenticators': Attach('The authenticator devices to use for '
                                 'validating users and passwords',
                                 Authenticator, multiple=True),
    }

    parameters = {
        'server':         Param('Address to bind to (host or host[:port])',
                                type=host(defaultport=DEFAULT_PORT),
                                mandatory=True,
                                ext_desc='The default port is ``1301``.'),
        'servercls':      Param('Server class used for creating transports '
                                'to each client',
                                type=str, mandatory=False,
                                default='nicos.services.daemon.proto.classic.'
                                'Server'),
        'serializercls':  Param('Serializer class used for serializing '
                                'messages transported from/to the server',
                                type=str, mandatory=False,
                                default='nicos.protocols.daemon.classic.'
                                'ClassicSerializer'),
        'maxlogins':      Param('Maximum number of simultaneous clients '
                                'served', type=int,
                                default=10),
        'updateinterval': Param('Interval for watch expressions checking and'
                                ' sending updates to the clients',
                                type=float, unit='s', default=0.2),
        'trustedhosts':   Param('A list of trusted hosts allowed to log in',
                                type=listof(str),
                                ext_desc='An empty list means all hosts are '
                                'allowed.'),
        'simmode':        Param('Whether to always start in dry run mode',
                                type=bool),
        'autosimulate':   Param('Whether to simulate scripts when running them',
                                type=bool, default=False)
    }

    def doInit(self, mode):
        # import server and serializer class
        servercls = importString(self.servercls)
        serialcls = importString(self.serializercls)

        self._stoprequest = False
        # the controller represents the internal script execution machinery
        if self.autosimulate and not config.sandbox_simulation:
            raise ConfigurationError('autosimulation configured but sandbox'
                                     ' deactivated')

        self._controller = ExecutionController(self.log, self.emit_event,
                                               'startup', self.simmode,
                                               self.autosimulate)

        # cache log messages emitted so far
        self._messages = []

        host, port = parseHostPort(self.server, DEFAULT_PORT)

        # create server (transport + serializer)
        self._server = servercls(self, (host, port), serialcls())

        self._watch_worker = createThread('daemon watch monitor',
                                          self._watch_entry)

    def _watch_entry(self):
        """
        This thread checks for watch value changes periodically and sends out
        events on changes.
        """
        # pre-fetch attributes for speed
        ctlr, intv, emit, sleep = self._controller, self.updateinterval, \
            self.emit_event, time.sleep
        lastwatch = {}
        while not self._stoprequest:
            sleep(intv)
            # new watch values?
            watch = ctlr.eval_watch_expressions()
            if watch != lastwatch:
                emit('watch', watch)
                lastwatch = watch

    def emit_event(self, event, data, blobs=None):
        """Emit an event to all handlers."""
        self._server.emit(event, data, blobs or [])

    def emit_event_private(self, event, data, blobs=None):
        """Emit an event to only the calling handler."""
        handler = self._controller.get_current_handler()
        if handler:
            self._server.emit(event, data, blobs or [], handler=handler)

    def statusinfo(self):
        self.log.info('got SIGUSR2 - current stacktraces for each thread:')
        active = threading._active
        for tid, frame in list(sys._current_frames().items()):
            if tid in active:
                name = active[tid].getName()
            else:
                name = str(tid)
            self.log.info('%s: %s', name, formatExtendedStack(frame))

    def start(self):
        """Start the daemon's server."""
        self.log.info('NICOS daemon v%s started, starting server on %s',
                      nicos_version, self.server)
        # startup the script thread
        self._controller.start_script_thread()
        self._worker = createThread('daemon server', self._server.start,
                                    args=(self._long_loop_delay,))

    def wait(self):
        while not self._stoprequest:
            time.sleep(self._long_loop_delay)
        self._worker.join()

    def quit(self, signum=None):
        self.log.info('quitting on signal %s...', signum)
        self._stoprequest = True
        self._server.stop()
        self._worker.join()
        self._server.close()

    def current_script(self):
        return self._controller.current_script

    def current_user(self):
        return getattr(self._controller.thread_data, 'user', system_user)

    def get_authenticators(self):
        return self._attached_authenticators
