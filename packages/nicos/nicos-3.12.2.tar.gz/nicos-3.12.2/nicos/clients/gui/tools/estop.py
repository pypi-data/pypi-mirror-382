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

"""Always-on-top emergency stop button."""

from nicos.clients.gui.utils import SettingGroup
from nicos.guisupport.qt import QAbstractButton, QByteArray, QHBoxLayout, \
    QIcon, QMainWindow, QPainter, QPoint, QSize, Qt, QWidget


class PicButton(QAbstractButton):
    def __init__(self, icon, parent=None):
        QAbstractButton.__init__(self, parent)
        self.icon = icon
        self._size = QSize(100, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        mode = QIcon.Mode.Active if self.isDown() else QIcon.Mode.Normal
        pixmap = self.icon.pixmap(self._size, mode)
        painter.drawPixmap(
            QPoint(0, 0),
            pixmap.scaled(event.rect().size(),
                          Qt.AspectRatioMode.KeepAspectRatio))

    def sizeHint(self):
        return self._size

    def maximumSize(self):
        return self._size


class EmergencyStopTool(QMainWindow):
    """A small window with a big "emergency stop" button.

    This window will stay on top of other windows, and when clicked triggers
    an "immediate stop" action in NICOS.
    """

    def __init__(self, parent, client, **settings):
        QMainWindow.__init__(self, parent)
        self.client = client
        self.setWindowTitle(' ')  # window title is unnecessary
        flags = self.windowFlags()
        flags |= Qt.WindowType.WindowStaysOnTopHint
        flags ^= Qt.WindowType.WindowMinimizeButtonHint
        self.setWindowFlags(flags)

        self.sgroup = SettingGroup('EstopTool')
        with self.sgroup as settings:
            self.restoreGeometry(settings.value('geometry', '', QByteArray))

        icon = QIcon(':/estop')
        icon.addFile(':/estopdown', mode=QIcon.Mode.Active)
        self.btn = PicButton(icon, self)

        widget = QWidget(self)
        layout = QHBoxLayout()
        layout.addWidget(self.btn)
        layout.setContentsMargins(3, 3, 3, 3)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.btn.clicked.connect(self.dostop)
        self.setFixedSize(self.minimumSize())
        self.show()

    def dostop(self):
        self.client.tell('emergency')

    def _saveSettings(self):
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())

    def closeEvent(self, event):
        self._saveSettings()
        self.deleteLater()

    def __del__(self):
        # there is a bug in Qt where closeEvent isn't called when the
        # main window is closed, so we try again here
        self._saveSettings()
