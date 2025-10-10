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

"""Directives to document daemon commands and events."""

from docutils.statemachine import StringList
from sphinx.domains.python import PyFunction, PyVariable
from sphinx.util.docfields import Field
from sphinx.util.docstrings import prepare_docstring

from nicos.services.daemon.handler import command_wrappers
from nicos.utils import formatArgs


class DaemonCommand(PyFunction):
    """Directive for daemon command description."""

    def handle_signature(self, sig, signode):
        self.object = command_wrappers[sig].orig_function
        sig = '%s%s' % (sig, formatArgs(self.object, strip_self=True))
        return PyFunction.handle_signature(self, sig, signode)

    def needs_arglist(self):
        return True

    def get_index_text(self, modname, name_cls):
        return '%s (daemon command)' % name_cls[0]

    def before_content(self):
        dstring = prepare_docstring(self.object.__doc__ or '')
        # overwrite content of directive
        self.content = StringList(dstring)
        PyFunction.before_content(self)


class DaemonEvent(PyVariable):
    """Directive for daemon command description."""

    doc_field_types = [
        Field('arg', label='Argument', has_arg=False, names=('arg',)),
    ]

    def needs_arglist(self):
        return False

    def get_index_text(self, modname, name_cls):
        return '%s (daemon event)' % name_cls[0]


def setup(app):
    app.add_directive('daemoncmd', DaemonCommand)
    app.add_directive('daemonevt', DaemonEvent)
    return {'parallel_read_safe': True,
            'version': '0.1.0'}
