import configparser

from utils.templates import *

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QLineEdit


class SocketSettingsWindow(QWidget):
    def __init__(self, mainUi, currentHostname, currentPort, currentStateDelay, currentTableDelay, currentPlotsDelay,
                 currentReconnectDelay):
        super(SocketSettingsWindow, self).__init__()
        uic.loadUi('uiFiles/socket.ui', self)
        self.mainUi = mainUi

        self.currentHostname = currentHostname
        self.currentPort = currentPort
        self.currentStateDelay = currentStateDelay
        self.currentTableDelay = currentTableDelay
        self.currentPlotDelay = currentPlotsDelay
        self.currentReconnectDelay = currentReconnectDelay

        self.onInit()

    def onInit(self):
        self.submitButton.clicked.connect(self.submit)
        self.setWindowTitle(self.mainUi.config.get('LOCALE', 'socketSettings'))

        self.hostnameLineEdit.setText(self.currentHostname) if self.currentHostname != '' else None
        self.portLineEdit.setText(self.currentPort) if self.currentPort != '' else None
        self.stateDelayLineEdit.setText(str(self.currentStateDelay)) if int(self.currentStateDelay) else None
        self.tableDelayLineEdit.setText(str(self.currentTableDelay)) if int(self.currentTableDelay) else None
        self.plotDelayLineEdit.setText(str(self.currentPlotDelay)) if int(self.currentPlotDelay) else None
        self.reconnectDelayLineEdit.setText(str(self.currentReconnectDelay)) if int(self.currentReconnectDelay) else None

    def isHostnameValid(self):
        return re.fullmatch(r'\d+\.\d+\.\d+\.\d+', self.hostnameLineEdit.text())

    def isPortValid(self):
        return re.fullmatch(r'\d+', self.portLineEdit.text())

    def isDelaysValid(self):
        return re.fullmatch(r'\d+', self.stateDelayLineEdit.text()) \
               and re.fullmatch(r'\d+', self.tableDelayLineEdit.text()) \
               and re.fullmatch(r'\d+', self.plotDelayLineEdit.text())

    def submit(self):
        hostname = self.hostnameLineEdit.text()
        port = self.portLineEdit.text()
        stateDelay = self.stateDelayLineEdit.text()
        tableDelay = self.tableDelayLineEdit.text()
        plotDelay = self.plotDelayLineEdit.text()
        reconnectDelay = self.reconnectDelayLineEdit.text()

        if not self.isHostnameValid():
            self.mainUi.showWarning(self.mainUi.config.get('LOCALE', 'wrongHostname'))
        elif not self.isPortValid():
            self.mainUi.showWarning(self.mainUi.config.get('LOCALE', 'wrongPort'))
        elif not self.isDelaysValid():
            self.mainUi.showWarning(self.mainUi.config.get('LOCALE', 'wrongDelay'))
        else:
            self.mainUi.hostname = hostname
            self.mainUi.port = port
            self.mainUi.updateServerAddress()
            self.mainUi.updateSettings()
            self.mainUi.updateDelays(stateDelay, tableDelay, plotDelay, reconnectDelay)
            self.mainUi.statusBar.showMessage(self.mainUi.config.get('LOCALE', 'addressUpdatedSuccessfully'), 10000)
            self.close()
