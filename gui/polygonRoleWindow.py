import configparser

from utils.templates import *

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem, QDialog


class PolygonRoleWindow(QDialog):
    def __init__(self, mainUi):
        super(PolygonRoleWindow, self).__init__()
        uic.loadUi('uiFiles/polygonRole.ui', self)

        self.mainUi = mainUi

        self.submitButton.clicked.connect(self.submit)

        self.onInit()

    def onInit(self):
        self.setWindowTitle(self.mainUi.config.get('LOCALE', 'selectRole'))
        fillComboBoxByRoles(self.mainUi.objectRolesDict, self.rolesComboBox)

    def submit(self):
        newObject = self.mainUi.objectTree.selectedItems()[0]
        selectedRole = self.rolesComboBox.currentText()  # in this case role == assert

        try:
            role = getRoleByAssert(self.mainUi.currentLocale, selectedRole)
            created = self.mainUi.totalCreated[getRoleByAssert(self.mainUi.currentLocale, selectedRole)]
            newObject.setText(0, f'{selectedRole}_{created+1}')
            self.mainUi.totalCreated.update({f'{role}': created+1})
        except KeyError:
            created = 0
            role = getRoleByAssert(self.mainUi.currentLocale, selectedRole)
            newObject.setText(0, selectedRole)
            self.mainUi.totalCreated.update({f'{role}': created})

        self.mainUi.updatePolygonPlots()
        self.close()


