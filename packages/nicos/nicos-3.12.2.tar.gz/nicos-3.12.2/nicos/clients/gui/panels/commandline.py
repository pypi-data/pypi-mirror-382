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

"""NICOS GUI command line input component."""

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, modePrompt
from nicos.guisupport.utils import setBackgroundColor


class CommandLinePanel(Panel):
    """Provides just an input box for entering commands and no output view."""

    panelName = 'CommandLinePanel'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/commandline.ui')

        self.commandInput.history = self.cmdhistory
        self.commandInput.completion_callback = self.completeInput

        client.initstatus.connect(self.on_client_initstatus)
        client.mode.connect(self.on_client_mode)
        client.experiment.connect(self.on_client_experiment)

    def setViewOnly(self, viewonly):
        self.commandInput.setEnabled(not viewonly)

    def loadSettings(self, settings):
        self.cmdhistory = settings.value('cmdhistory') or []

    def saveSettings(self, settings):
        # only save 100 entries of the history
        cmdhistory = self.commandInput.history[-100:]
        settings.setValue('cmdhistory', cmdhistory)

    def getMenus(self):
        return []

    def setCustomStyle(self, font, back):
        self.commandInput.idle_color = back
        self.commandInput.setFont(font)
        self.label.setFont(font)
        setBackgroundColor(self.commandInput, back)

    def updateStatus(self, status, exception=False):
        self.commandInput.setStatus(status)

    def completeInput(self, fullstring, lastword):
        try:
            return self.client.ask('complete', fullstring, lastword,
                                   default=[])
        except Exception:
            return []

    def on_client_mode(self, mode):
        self.label.setText(modePrompt(mode))

    def on_client_initstatus(self, state):
        self.on_client_mode(state['mode'])

    def on_client_experiment(self, data):
        (_, proptype) = data
        if proptype == 'user':
            # only clear when switching TO a user experiment
            self.commandInput.history = []

    def on_commandInput_execRequested(self, script, action):
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
        self.commandInput.setText('')
