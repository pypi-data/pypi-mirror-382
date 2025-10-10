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

"""Dialog for selecting an instrument guiconfig."""

from os import path
from pathlib import Path

from nicos import config
from nicos.clients.gui.utils import SettingGroup, loadUi
from nicos.guisupport.qt import QDialog, QDialogButtonBox, QIcon, \
    QTreeWidgetItem


class InstrSelectDialog(QDialog):
    """A dialog to request connection parameters."""

    def __init__(self, reason, parent=None):
        QDialog.__init__(self, parent)
        loadUi(self, 'dialogs/instr_select.ui')
        icon = QIcon(':/appicon-16')
        if reason:
            self.reasonLbl.setText(reason)
        else:
            self.reasonLbl.hide()
            self.saveBox.hide()

        self.confTree.itemDoubleClicked.connect(self.handleDoubleClick)
        self.confTree.currentItemChanged.connect(self.handleSelection)
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Ok).setDisabled(True)
        tree = {}

        for entry in sorted(Path(config.nicos_root).rglob('guiconfig.py')):
            parent = entry.relative_to(config.nicos_root).parent
            if not parent.parts[0].startswith('nicos_'):
                continue
            ptree = tree
            for part in parent.parts:
                ptree = ptree.setdefault(part, {})
            ptree['config'] = entry

        def add_subitems(pitem, tree):
            for k, v in tree.items():
                item = QTreeWidgetItem(pitem, [k])
                if 'config' in v:
                    item.setData(0, QTreeWidgetItem.ItemType.UserType,
                                 v['config'])
                else:
                    add_subitems(item, v)

        for k, v in tree.items():
            pkgitem = QTreeWidgetItem(self.confTree, [k])
            pkgitem.setIcon(0, icon)
            if 'config' in v:
                pkgitem.setData(0, QTreeWidgetItem.ItemType.UserType,
                                v.pop('config'))
            add_subitems(pkgitem, v)

    def handleSelection(self, cur, _prev):
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            cur.data(0, QTreeWidgetItem.ItemType.UserType) is not None)

    def handleDoubleClick(self, item, _col):
        if item.data(0, QTreeWidgetItem.ItemType.UserType):
            self.accept()

    @classmethod
    def select(cls, reason='', force=False):
        with SettingGroup('Instrument') as settings:
            configfile = None if force else \
                (settings.value('guiconfig') or None)
            while not (configfile and path.isfile(configfile)):
                dlg = cls(reason)
                result = dlg.exec()
                if not result:
                    return None
                items = dlg.confTree.selectedItems()
                if items:
                    configfile = items[0].data(
                        0, QTreeWidgetItem.ItemType.UserType)
                    if force or dlg.saveBox.isChecked():
                        settings.setValue('guiconfig', configfile)
            return configfile
