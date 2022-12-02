import configparser

from utils.templates import *

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem


class PolygonRoleWindow(QWidget):
    def __init__(self, mainUi):
        super(PolygonRoleWindow, self).__init__()
        uic.loadUi('uiFiles/polygonRole.ui', self)

        self.mainUi = mainUi

        self.submitButton.clicked.connect(self.submit)

        self.onInit()

    def onInit(self):
        self.config = configparser.ConfigParser()
        self.config.read(f'locales/{self.mainUi.currentLocale}.ini')
        self.setWindowTitle(self.config.get('LOCALE', 'selectRole'))
        fillComboBoxByRoles(self.mainUi.objectRolesDict, self.rolesComboBox)

    def submit(self):
        newObject = self.mainUi.objectTree.selectedItems()[0]
        selectedRole = self.rolesComboBox.currentText()
        newObject.child(getFieldIndex(newObject, 'role')).setText(1, str(selectedRole))
        self.close()


