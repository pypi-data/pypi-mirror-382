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
#   Stefan Mathis <stefan.mathis@psi.ch>
#   Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

"""AMOR specific commands and routines"""

import subprocess

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.scan import ADDSCANHELP0, ADDSCANHELP2, _handleScanArgs, \
    _infostr

from nicos_sinq.amor.scan import WallTimeScan
from nicos_sinq.devices.detector import SinqDetector


@usercommand
def synchronize_daq():
    """Synchronize the time on the data acquisition computer with that of the
    ring modules.

    The local clocks on the ESS data acquisition PC and on the ring modules go
    quickly out of sync, which causes time offsets between the neutron signal
    and the proton current signal. To combat this, it is necessary to
    synchronize the clocks before each measurement with this command.
    """
    with subprocess.Popen(['ssh', '-t', 'essdaq@det-efu02'],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE) as sshProcess:

        command = b"""
                  essdaq; cd /home/essdaq/detg_git/dgro_master/
                  python_slow_ctl2/utgard_kc705_vmm; sh update_rmm_time.sh
                  """
        (_, error) = sshProcess.communicate(command)
        if error:
            session.log.error('Synchronizing the DAQ time failed. Check if '
                              'the computer det-efu02 is online.')
        else:
            session.log.info('Synchronization successfull.')


@usercommand
@helparglist('numpoints, walltime, ...')
def walltimecount(numpoints, walltime, *args, **kwargs):
    """Count a number of times for the given amount of time on wall.

    "numpoints" can be -1 to scan for unlimited points (break using Ctrl-C or
    the GUI to quit).

    "walltime" provides the time in seconds

    Example:

    >>> walltimecount(500, 10)  # counts 500 times, every count for 10 seconds

    A special "delay" argument is supported to allow time delays between two
    points:

    >>> walltimecount(500, 2, delay=5)
    """
    scanstr = _infostr('walltimecount', (numpoints, walltime, ) + args, kwargs)
    preset, scaninfo, detlist, envlist, move, multistep = \
        _handleScanArgs(args, kwargs, scanstr)

    # Get AMOR detector
    if not detlist:
        detlist = session.experiment.detectors

    detector = None
    for det in detlist:
        if isinstance(det, SinqDetector):
            detector = det

    if not detector:
        session.log.error('Detector not found in the detector list')

    # Set the beam threshold to 0
    oldthreshold = detector.threshold

    # Complete the scan
    scan = WallTimeScan([], [], numpoints, walltime, move, multistep, detlist,
                        envlist, preset, scaninfo)
    scan.run()

    # Reset the beam threshold to oldvalue
    detector.threshold = oldthreshold


walltimecount.__doc__ += \
    (ADDSCANHELP0 + ADDSCANHELP2).replace('scan(dev, ', 'walltimecount(5, ')


@usercommand
@helparglist('state')
def spin(state):
    """Change the spin state to + or -.

    Example:

    Following command brings spin state to +

    >>> spin('+')
    """
    if state not in ('+', '-'):
        session.log.error('Expected only +/- as the state for spin')

    flipper = session.getDevice('SpinFlipper')

    if state == '+':
        flipper.maw('SPIN UP')
    elif state == '-':
        flipper.maw('SPIN DOWN')
