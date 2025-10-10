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

import ast

from nicos.guisupport.led import ClickableOutputLed
from nicos.guisupport.qt import QCheckBox, Qt
from nicos.guisupport.widget import NicosWidget, PropDef


class PushButton(ClickableOutputLed):

    designer_description = 'Simulation of a push button with a light'
    designer_icon = ':/leds/blue_on'

    def __init__(self, parent=None, designMode=False):
        ClickableOutputLed.__init__(self, parent, designMode)

    def on_keyChange(self, key, value, time, expired):
        if value == self._stateInactive:
            self.ledStatus = False
        else:
            self.ledStatus = True
        if self._goalval is not None:
            value = self._goalval
        self.current = value

    def mousePressEvent(self, event):

        ledColor = self.ledColor

        ClickableOutputLed.mousePressEvent(self, event)

        self.ledColor = ledColor


class SinglePushButton(PushButton):

    designer_description = 'Simulation of a push button with a light and only'\
                           ' one state to switch On or Off'
    designer_icon = ':/leds/yellow_on'

    toState = PropDef('toState', str, '1', 'Target for action')

    def __init__(self, parent=None, designMode=False):
        self._stateTo = 1
        PushButton.__init__(self, parent, designMode)

    def propertyUpdated(self, pname, value):
        PushButton.propertyUpdated(self, pname, value)

        if pname == 'toState':
            if isinstance(value, str):
                self._stateTo = value
            else:
                self._stateTo = ast.literal_eval(value) if value else 1

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            if self._client:
                self._client.run('move(%s, %r)' % (self.dev, self._stateTo))
        event.accept()


class CheckBox(QCheckBox, NicosWidget):
    designer_description = 'Shows and toggles a boolean parameter'

    key = PropDef('key', str, '', 'Key to use as the value')
    onCommand = PropDef('onCommand', str, '', 'Command to run for "on"')
    offCommand = PropDef('offCommand', str, '', 'Command to run for "off"')

    def __init__(self, parent=None, designMode=False):
        QCheckBox.__init__(self, parent)
        NicosWidget.__init__(self)
        self.clicked.connect(self.on_clicked)

    def registerKeys(self):
        self.registerKey(self.props['key'])

    def on_keyChange(self, key, value, time, expired):
        if expired:
            return
        self.setChecked(bool(value))

    def on_clicked(self, on):
        if on:
            self._client.run(self.props['onCommand'])
        else:
            self._client.run(self.props['offCommand'])
