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

"""NICOS GUI settings window."""

from nicos.clients.base import ConnectionData
from nicos.clients.gui.dialogs.instr_select import InstrSelectDialog
from nicos.clients.gui.utils import DlgUtils, SettingGroup, dialogFromUi, \
    loadUi, splitTunnelString
from nicos.guisupport.qt import QDialog, QListWidgetItem, QTreeWidgetItem, \
    pyqtSlot


class SettingsDialog(DlgUtils, QDialog):
    def __init__(self, main):
        QDialog.__init__(self, main)
        DlgUtils.__init__(self, 'Settings')
        loadUi(self, 'dialogs/settings.ui')
        self.tunnelUserLabel.setVisible(False)
        self.tunnelUserInput.setVisible(False)
        self.tunnelHostLabel.setVisible(False)
        self.tunnelHostInput.setVisible(False)
        self.main = main
        self.sgroup = main.sgroup

        genitem = QTreeWidgetItem(self.settingsTree, ['General'], -2)
        QTreeWidgetItem(self.settingsTree, ['Connection presets'], -1)
        self.settingsTree.setCurrentItem(genitem)
        self.stacker.setCurrentIndex(0)

        # general page
        self.instrument.setText(main.instrument)
        self.confirmExit.setChecked(main.confirmexit)
        self.warnWhenAdmin.setChecked(main.warnwhenadmin)
        self.showTrayIcon.setChecked(main.showtrayicon)
        self.autoReconnect.setChecked(main.autoreconnect)
        self.autoSaveLayout.setChecked(main.autosavelayout)
        self.manualSaveLayout.setChecked(not main.autosavelayout)
        self.allowOutputLineWrap.setChecked(main.allowoutputlinewrap)

        self.useTunnelCheckBox.setChecked(bool(main.tunnel))
        tunnelUser, tunnelHost, _ = splitTunnelString(main.tunnel)
        if tunnelUser:
            self.tunnelUserInput.setText(tunnelUser)
        if tunnelHost:
            self.tunnelHostInput.setText(tunnelHost)

        # connection data page
        self.connpresets = main.connpresets
        for setting, cdata in main.connpresets.items():
            QListWidgetItem(setting + ' (%s:%s)' % (cdata.host, cdata.port),
                            self.settinglist).setData(32, setting)

    def saveSettings(self):
        self.main.instrument = self.instrument.text()
        self.main.confirmexit = self.confirmExit.isChecked()
        self.main.warnwhenadmin = self.warnWhenAdmin.isChecked()
        self.main.showtrayicon = self.showTrayIcon.isChecked()
        self.main.autoreconnect = self.autoReconnect.isChecked()
        self.main.autosavelayout = self.autoSaveLayout.isChecked()
        self.main.allowoutputlinewrap = self.allowOutputLineWrap.isChecked()
        self.main.tunnel = ''
        if self.useTunnelCheckBox.isChecked():
            tunnelHost = self.tunnelHostInput.text()
            tunnelUser = self.tunnelUserInput.text()
            if tunnelHost:
                if tunnelUser:
                    self.main.tunnel = f'{tunnelUser}@{tunnelHost}'
                else:
                    self.main.tunnel = f'{tunnelHost}'
        with self.sgroup as settings:
            settings.setValue(
                'connpresets_new', {k: v.serialize() for (k, v)
                                    in self.connpresets.items()})
            settings.setValue('instrument', self.main.instrument)
            settings.setValue('confirmexit', self.main.confirmexit)
            settings.setValue('warnwhenadmin', self.main.warnwhenadmin)
            settings.setValue('showtrayicon', self.main.showtrayicon)
            settings.setValue('autoreconnect', self.main.autoreconnect)
            settings.setValue('autosavelayout', self.main.autosavelayout)
            settings.setValue('allowoutputlinewrap', self.main.allowoutputlinewrap)
        if self.main.showtrayicon:
            self.main.trayIcon.show()
        else:
            self.main.trayIcon.hide()

    @pyqtSlot()
    def on_saveLayoutBtn_clicked(self):
        self.main.saveWindowLayout()
        for win in self.main.windows.values():
            win.saveWindowLayout()
        self.showInfo('The window layout was saved.')

    @pyqtSlot()
    def on_selectConfigBtn_clicked(self):
        InstrSelectDialog.select(force=True)

    @pyqtSlot()
    def on_clearConfigBtn_clicked(self):
        with SettingGroup('Instrument') as settings:
            settings.remove('guiconfig')
        self.showInfo('Default instrument GUI configuration has been cleared.')

    @pyqtSlot()
    def on_settingAdd_clicked(self):
        dlg = dialogFromUi(self, 'dialogs/settings_conn.ui')
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        if not dlg.name.text():
            return
        name = dlg.name.text()
        while name in self.connpresets:
            name += '_'
        cdata = ConnectionData(
            dlg.host.text(), dlg.port.value(), dlg.login.text(), None,
            dlg.viewonly.isChecked(), dlg.expertmode.isChecked())
        self.connpresets[name] = cdata
        QListWidgetItem(name + ' (%s:%s)' % (cdata.host, cdata.port),
                        self.settinglist).setData(32, name)

    @pyqtSlot()
    def on_settingDel_clicked(self):
        item = self.settinglist.currentItem()
        if item is None:
            return
        del self.connpresets[item.data(32)]
        self.settinglist.takeItem(self.settinglist.row(item))

    @pyqtSlot()
    def on_settingEdit_clicked(self):
        item = self.settinglist.currentItem()
        if item is None:
            return
        cdata = self.connpresets[item.data(32)]
        dlg = dialogFromUi(self, 'dialogs/settings_conn.ui')
        dlg.name.setText(item.data(32))
        dlg.name.setEnabled(False)
        dlg.host.setText(cdata.host)
        dlg.port.setValue(cdata.port)
        dlg.login.setText(cdata.user)
        dlg.viewonly.setChecked(cdata.viewonly)
        dlg.expertmode.setChecked(cdata.expertmode)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        cdata.host = dlg.host.text()
        cdata.port = dlg.port.value()
        cdata.user = dlg.login.text()
        cdata.viewonly = dlg.viewonly.isChecked()
        cdata.expertmode = dlg.expertmode.isChecked()
        item.setText('%s (%s:%s)' % (dlg.name.text(), cdata.host, cdata.port))

    def on_settingsTree_itemClicked(self, item, column):
        self.on_settingsTree_itemActivated(item, column)

    def on_settingsTree_itemActivated(self, item, column):
        if self.stacker.count() > 3:
            self.stacker.removeWidget(self.stacker.widget(3))
        if item.type() == -2:
            self.stacker.setCurrentIndex(0)
        elif item.type() == -1:
            self.stacker.setCurrentIndex(1)
        elif item.type() == 0:
            self.stacker.setCurrentIndex(2)

    @pyqtSlot()
    def on_useTunnelCheckBox_toggled(self, value):
        if not value:
            self.tunnelHostInput.setText('')
            self.tunnelUserInput.setText('')
