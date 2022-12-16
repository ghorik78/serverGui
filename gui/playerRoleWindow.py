import configparser

from utils.templates import *

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QDialog


class PlayerRoleWindow(QDialog):
    def __init__(self, mainUi):
        super(PlayerRoleWindow, self).__init__()
        uic.loadUi('uiFiles/playerRole.ui', self)
        self.mainUi = mainUi
        self.onInit()

    def onInit(self):
        self.config = configparser.ConfigParser()
        self.config.read(f'locales/{self.mainUi.currentLocale}.ini')
        self.submitButton.clicked.connect(self.submit)
        self.setWindowTitle(self.config.get('LOCALE', 'selectRole'))
        fillComboBoxByRoles(self.mainUi.playerRolesDict, self.rolesComboBox)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        newPlayer = self.mainUi.playerTree.selectedItems()[0] if len(self.mainUi.playerTree.selectedItems()) else None
        self.mainUi.playerTree.invisibleRootItem().removeChild(newPlayer)

    def submit(self):
        newPlayer = self.mainUi.playerTree.selectedItems()[0]
        selectedRole = self.rolesComboBox.currentText()
        newPlayer.child(getQtFieldIndex(newPlayer, 'role_obj')).setText(1, str(selectedRole))
        self.mainUi.updateController()
        self.mainUi.setUnselected(self.mainUi.playerTree.selectedItems())
        self.close()


