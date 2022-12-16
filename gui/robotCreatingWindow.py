from database.database import *

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QDialog


class RobotCreatingWindow(QDialog):
    def __init__(self, mainUi):
        super(RobotCreatingWindow, self).__init__()
        uic.loadUi('uiFiles/robotList.ui', self)
        self.mainUi = mainUi
        self.onInit()

    def onInit(self):
        self.setWindowTitle(self.mainUi.config.get('LOCALE', 'selectRole'))
        self.submitButton.clicked.connect(self.submit)
        self.prepareRobotList()

    def prepareRobotList(self):
        self.robotComboBox.addItems(getCreatedRobots())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        newRobot = self.mainUi.robotTree.selectedItems()[0] if len(self.mainUi.robotTree.selectedItems()) else None
        self.mainUi.robotTree.invisibleRootItem().removeChild(newRobot)

    def submit(self):
        newRobot = self.mainUi.robotTree.selectedItems()[0]
        selectedRobot = self.robotComboBox.currentText()
        newRobot.setText(0, selectedRobot)
        self.mainUi.updateController()
        self.mainUi.setUnselected(self.mainUi.robotTree.selectedItems())
        self.close()
