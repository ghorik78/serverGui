import configparser

from utils.templates import *

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QLineEdit


class SocketSettingsWindow(QWidget):
    def __init__(self, mainUi, currentHostname, currentPort):
        super(SocketSettingsWindow, self).__init__()
        uic.loadUi('uiFiles/socket.ui', self)
        self.mainUi = mainUi

        self.currentHostname = currentHostname
        self.currentPort = currentPort

        self.onInit()

    def onInit(self):
        self.submitButton.clicked.connect(self.submit)
        self.setWindowTitle(self.mainUi.config.get('LOCALE', 'socketSettings'))

        if (self.currentHostname != '') and (self.currentPort != ''):
            self.hostnameLineEdit.setText(self.currentHostname)
            self.portLineEdit.setText(self.currentPort)

    def submit(self):
        hostname = self.hostnameLineEdit.text()
        port = self.portLineEdit.text()

        if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+', hostname):
            self.mainUi.showWarning(self.mainUi.config.get('LOCALE', 'wrongHostname'))
        elif not re.fullmatch(r'\d+', port):
            self.mainUi.showWarning(self.mainUi.config.get('LOCALE', 'wrongPort'))
        else:
            self.mainUi.hostname = hostname
            self.mainUi.port = port
            self.mainUi.updateServerAddress()
            self.mainUi.updateSettings()
            self.mainUi.statusBar.showMessage(self.mainUi.config.get('LOCALE', 'addressUpdatedSuccessfully'), 10000)
            self.close()


