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

"""Module for output/logging user commands."""

from nicos import session
from nicos.commands import helparglist, hiddenusercommand, parallel_safe, \
    usercommand

__all__ = [
    'printdebug', 'printinfo', 'printwarning', 'printerror', 'printexception',
]


@hiddenusercommand
@helparglist('message, ...')
@parallel_safe
def printdebug(*msgs):
    """Print a debug message."""
    session.log.debug(' '.join('%s' for _ in msgs), *msgs)


@usercommand
@helparglist('message, ...')
@parallel_safe
def printinfo(*msgs):
    """Print a message.

    This function is equivalent to the standard Python "print" statement.
    """
    session.log.info(' '.join('%s' for _ in msgs), *msgs)


@usercommand
@helparglist('message, ...')
@parallel_safe
def printwarning(*msgs):
    """Print a warning message.

    In the output history, the message will be highlighted as a warning and
    therefore be more visible than normal "info" messages.

    Example:

    >>> printwarning('count rate < 1000 Hz')
    """
    session.log.warning(' '.join('%s' for _ in msgs), *msgs)


@usercommand
@helparglist('message, ...')
@parallel_safe
def printerror(*msgs):
    """Print an error message.

    In the output history, the message will be highlighted as an error (usually
    in red and bold) and therefore be very visible.

    Example:

    >>> printerror('scan failed, repeating this run')
    """
    session.log.error(' '.join('%s' for _ in msgs), *msgs)


@hiddenusercommand
@helparglist('message, ...')
@parallel_safe
def printexception(*msgs):
    """Print an error message, and add info about the last exception."""
    session.log.exception(' '.join('%s' for _ in msgs), *msgs)
