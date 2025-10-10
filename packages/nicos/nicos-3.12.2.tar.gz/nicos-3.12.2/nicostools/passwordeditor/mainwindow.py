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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************

import hashlib
import logging
from os import path

from nicos import config
from nicos.guisupport.qt import QFileDialog, QMainWindow, QMessageBox, uic

from .daemonsetup import DaemonSetup
from .user import User
from .userdialog import UserDialog

config.apply()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        uic.loadUi(path.join(path.dirname(path.abspath(__file__)),
                             'ui', 'mainwindow.ui'), self)

        self.className = ''     # name of the devices class in auth tuple
        self.group = ''         # name of the group defined in the setup file
        self.description = ''   # name of the description in the setup file
        self.authDict = {}      # dictionary containing info in auth tuple
        self.users = {}         # dict to store users while working

        self.actionLoad.triggered.connect(self.loadFile)
        self.actionSave.triggered.connect(self.save)
        self.actionPrintUsers.triggered.connect(self.debugUsers)
        self.actionShowDebug.triggered.connect(self.toggleDebug)

        self.menuBar.clear()
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuEdit)

        self.userList.currentItemChanged.connect(self.changeUser)
        self.pushButtonAddUser.clicked.connect(self.addUser)
        self.pushButtonDeleteUser.clicked.connect(self.deleteUser)
        self.pushButtonSaveConfig.clicked.connect(self.setConfig)
        self.pushButtonSaveUser.clicked.connect(self.setUserData)

        self.comboBoxHashing.activated.connect(self.changedConfig)
        self.lineEditUserName.textEdited.connect(self.changedUser)
        self.lineEditPassword.textEdited.connect(self.changedUser)
        self.comboBoxUserLevel.activated.connect(self.changedUser)

        # Initialize a logger required by setups.readSetup()
        self.log = logging.getLogger()
        self.setuppath = path.join(path.abspath('.'), 'nicos_mlz',
                                   config.instrument, 'setups', 'special',
                                   'daemon.py')
        self.setup = None
        self.readSetupFile(self.setuppath)

    def loadFile(self):
        # allows a user to specify the setup file to be parsed
        setupFile = QFileDialog.getOpenFileName(
            self,
            'Open Python script',
            path.expanduser('.'),
            'Python Files (*.py)')[0]

        if setupFile:
            self.readSetupFile(setupFile)

    def readSetupFile(self, pathToFile):
        # uses nicos.core.sessions.setups.readSetup() to read a setup file and
        # put the information in the self.info dictionary.
        while self.userList.count() > 1:
            self.userList.takeItem(1)

        self.setup = DaemonSetup(str(pathToFile))

        for userTuple in self.setup.getPasswordEntries():
            self.users[userTuple[0]] = User(userTuple[0], userTuple[1],
                                            userTuple[2])

        for key in self.users:
            self.userList.addItem(key)  # put users in gui (list widget)

        self.userList.setEnabled(True)
        self.comboBoxHashing.setEnabled(True)
        self.lineEditUserName.setEnabled(True)
        self.lineEditPassword.setEnabled(True)
        self.comboBoxUserLevel.setEnabled(True)
        self.pushButtonAddUser.setEnabled(True)
        self.pushButtonDeleteUser.setEnabled(True)

        self.userList.setCurrentRow(0)
        self.reloadConfig()
        self.setWindowTitle(pathToFile)

    def changeUser(self, user, previuousUser):
        # signal provides last item and current item
        self.pushButtonSaveUser.setEnabled(False)
        self.pushButtonSaveConfig.setEnabled(False)

        if self.userList.currentRow() == 0:  # if "Device Configuration...":
            self.userWidget.setVisible(False)
            self.infoWidget.setVisible(True)
            self.pushButtonDeleteUser.setEnabled(False)
            self.comboBoxHashing.setCurrentIndex(self.comboBoxHashing.findText(
                self.setup.getHashing()))
            return

        if not self.userWidget.isVisible():  # if previous selection was no user
            self.userWidget.setVisible(True)
            self.infoWidget.setVisible(False)
            self.pushButtonDeleteUser.setEnabled(True)

        currentUser = self.users[str(user.text())]
        self.lineEditUserName.setText(currentUser.userName)
        if currentUser.password:
            # to show 'there is a password, it's not empty'
            self.lineEditPassword.setText('abcdefg')
        else:
            self.lineEditPassword.clear()
        self.comboBoxUserLevel.setCurrentIndex(self.comboBoxUserLevel.findText(
            currentUser.userLevel))

    def reloadConfig(self):
        self.pushButtonDeleteUser.setEnabled(False)
        self.comboBoxHashing.setCurrentIndex(self.comboBoxHashing.findText(
            self.setup.getHashing()))

    def deleteUser(self):
        user = str(self.userList.currentItem().text())
        del self.users[user]  # remove from model
        self.userList.takeItem(self.userList.currentRow())  # remove from gui

    def addUser(self):
        dlg = UserDialog()
        if dlg.exec():
            username = str(dlg.lineEditUserName.text())
            if dlg.lineEditPassword.text().isEmpty():
                password = ''
            else:
                noHashPassword = str(dlg.lineEditPassword.text())
                if config.instrument != 'demo':
                    if self.setup.getHashing() == 'sha1':
                        password = str(hashlib.sha1(noHashPassword).hexdigest())
                    else:  # elif self.getHashing() == 'md5':
                        password = str(hashlib.md5(noHashPassword).hexdigest())
                else:
                    password = 'hashlib.%s(b%r).hexdigest()' % (
                        self.setup.getHashing(), str(noHashPassword))
            userlevel = str(dlg.comboBoxUserLevel.currentText())
            newUser = User(username, password, userlevel)
            self.users[username] = newUser
            self.userList.addItem(username)

    def hashingMsgbox(self):
        msgBox = QMessageBox()
        msgBox.setText('Changing the hashing requires you to enter all'
                       'passwords again.')
        msgBox.setInformativeText('Do you still want to change the hashing?\n'
                                  'WARNING: THIS WILL CLEAR ALL PASSWORDS.')
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok |
                                  QMessageBox.StandardButton.Cancel)
        msgBox.setDefaultButton(QMessageBox.StandardButton.Cancel)
        return msgBox.exec() == QMessageBox.StandardButton.Ok

    def setConfig(self):
        # method called when clicking save button in config widget.
        self.pushButtonSaveConfig.setEnabled(False)

        newHashing = str(self.comboBoxHashing.currentText())
        if newHashing != self.setup.getHashing():
            if self.hashingMsgbox():
                self.setup.setHashing(newHashing)
                self.removeAllPasswords()
            else:
                self.comboBoxHashing.setCurrentIndex(
                    self.comboBoxHashing.findText(self.setup.getHashing()))

    def setUserData(self):
        # method called when clicking save button in user widget.
        self.pushButtonSaveUser.setEnabled(False)

        # get the string of the currently selected user in GUI
        oldUserName = str(self.userList.currentItem().text())

        # get the new entered username
        newUserName = str(self.lineEditUserName.text())

        # update model
        # because users are identified by their name, the key in the dictionary
        # must be updated to the new name.
        self.users[newUserName] = self.users.pop(oldUserName)
        self.users[newUserName].userName = newUserName
        if self.lineEditPassword.text().isEmpty():
            password = ''
        else:
            noHashPassword = str(self.lineEditPassword.text())
            if self.setup.getHashing() == 'sha1':
                password = str(hashlib.sha1(noHashPassword).hexdigest())
            else:  # elif self.setup.getHashing() == 'md5':
                password = str(hashlib.md5(noHashPassword).hexdigest())
        self.users[newUserName].password = password
        self.users[newUserName].userLevel = str(self.comboBoxUserLevel.
                                                currentText())

        # update GUI
        self.userList.currentItem().setText(newUserName)

    def changedConfig(self):
        # called when changing lineEdits for className, group, description
        # or selection in comboBoxHashing changed
        if not self.pushButtonSaveConfig.isEnabled():
            self.pushButtonSaveConfig.setEnabled(True)

    def changedUser(self):
        # called when lineEditUserName, lineEditPassword, comoBoxUserLevel
        # change
        if not self.pushButtonSaveUser.isEnabled():
            self.pushButtonSaveUser.setEnabled(True)

    def removeAllPasswords(self):
        # called when hashing changes: It's neccessary to enter all passwords
        # again, so they can be hashed in the new way.
        for _, value in self.users.items():
            value.password = ''

    def toggleDebug(self):
        if self.actionShowDebug.isChecked():
            self.menuBar.clear()
            self.menuBar.addMenu(self.menuFile)
            self.menuBar.addMenu(self.menuEdit)
            self.menuBar.addMenu(self.menuDebug)
        else:
            self.menuBar.clear()
            self.menuBar.addMenu(self.menuFile)
            self.menuBar.addMenu(self.menuEdit)

    def debugUsers(self):
        for _, value in self.users.items():
            print(value.userName, value.password, value.userLevel)

    def saveAs(self):
        # open a file to save into, create empty output string
        filepath = QFileDialog.getSaveFileName(
            self,
            'Save as...',
            path.expanduser('.'),
            'Python script (*.py)')[0]
        if str(filepath):
            self._save(filepath)

    def save(self):
        pw = []
        for _, value in self.users.items():
            pw.append((value.userName, value.password, value.userLevel))
            self.setup.updatePasswordEntries(pw)
        self.setup.save()
