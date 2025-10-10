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

"""Session classes for simple and noninteractive use."""

import signal
import sys

from nicos import session
from nicos.core.constants import SLAVE
from nicos.core.sessions import Session
from nicos.utils import daemonize, removePidfile, setuser, writePidfile

try:
    import systemd.daemon
except ImportError:
    systemd = None


class NoninteractiveSession(Session):
    """
    Subclass of Session that configures the logging system for simple
    noninteractive usage.
    """

    autocreate_devices = False

    def _beforeStart(self, maindev, daemonized):
        pass

    @classmethod
    def _notify_systemd(cls, appname, status, ready=False):
        if hasattr(systemd.daemon, 'Notification'):
            # older module from PyPI
            systemd.daemon.notify(systemd.daemon.Notification.STATUS, status)
            if ready:
                systemd.daemon.notify(systemd.daemon.Notification.READY)
        else:
            # newer module from systemd package
            systemd.daemon.notify(('READY=1\n' if ready else '') +
                                  'STATUS=' + status)

    @classmethod
    def _get_maindev(cls, appname, maindevname, setupname):
        session.loadSetup(setupname or appname, allow_special=True,
                          raise_failed=True, autoload_system=False)
        return session.getDevice(maindevname or appname.capitalize())

    @classmethod
    def run(cls, appname, maindevname=None, setupname=None, pidfile=True,
            daemon=False, start_args=None):
        if daemon == 'systemd':
            cls._notify_systemd(appname, 'initializing session')
        elif daemon:
            daemonize()
        else:
            setuser()

        def quit_handler(signum, frame):
            maindev.quit(signum=signum)

        def reload_handler(signum, frame):
            if hasattr(maindev, 'reload'):
                maindev.reload()

        def status_handler(signum, frame):
            if hasattr(maindev, 'statusinfo'):
                maindev.statusinfo()

        session.__class__ = cls
        try:
            # pylint: disable=unnecessary-dunder-call
            session.__init__(appname, daemonized=daemon)
            maindev = cls._get_maindev(appname, maindevname, setupname)

            signal.signal(signal.SIGINT, quit_handler)
            signal.signal(signal.SIGTERM, quit_handler)
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, reload_handler)
                signal.signal(signal.SIGUSR2, status_handler)

            if pidfile and daemon != 'systemd':
                writePidfile(appname)

            session._beforeStart(maindev, daemonized=daemon)
        except Exception as err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print('Fatal error while initializing:', err, file=sys.stderr)
            return 1

        if daemon == 'systemd':
            cls._notify_systemd(appname, 'starting main device')

        start_args = start_args or ()
        maindev.start(*start_args)

        if daemon == 'systemd':
            cls._notify_systemd(appname, 'running', ready=True)

        # For services that don't run in a separate thread
        if hasattr(maindev, 'run_main_loop'):
            maindev.run_main_loop()

        maindev.wait()

        session.shutdown()
        if pidfile and daemon != 'systemd':
            removePidfile(appname)


class SingleDeviceSession(NoninteractiveSession):

    @classmethod
    def _get_maindev(cls, appname, maindevcls, setup):  # pylint: disable=arguments-renamed
        return maindevcls(appname, **setup)


class ScriptSession(Session):
    """
    Subclass of Session that allows for batch execution of scripts.
    """

    @classmethod
    def run(cls, setup, code, mode=SLAVE, appname='script'):
        session.__class__ = cls

        try:
            # pylint: disable=unnecessary-dunder-call
            session.__init__(appname)
        except Exception as err:
            try:
                session.log.exception('Fatal error while initializing')
            finally:
                print('Fatal error while initializing:', err, file=sys.stderr)
            return 1

        # Load the initial setup and handle becoming master.
        session.handleInitialSetup(setup, mode)

        # Execute the script code and shut down.
        exec(code, session.namespace)
        session.shutdown()
