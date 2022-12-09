import configparser

from utils.templates import *

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QDialog


class PlayerRoleWindow(QDialog):
    def __init__(self, mainUi):
        super(PlayerRoleWindow, self).__init__()
        uic.loadUi('uiFiles/playerRole.ui', self)

        self.mainUi = mainUi

        self.submitButton.clicked.connect(self.submit)

        self.onInit()

    def onInit(self):
        self.config = configparser.ConfigParser()
        self.config.read(f'locales/{self.mainUi.currentLocale}.ini')
        self.setWindowTitle(self.config.get('LOCALE', 'selectRole'))
        fillComboBoxByRoles(self.mainUi.playerRolesDict, self.rolesComboBox)

    def submit(self):
        newObject = self.mainUi.playerTree.selectedItems()[0]
        selectedRole = self.rolesComboBox.currentText()
        newObject.child(getFieldIndex(newObject, 'role_obj')).setText(1, str(selectedRole))
        self.mainUi.updateController()
        self.close()


