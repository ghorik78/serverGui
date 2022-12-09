from database.database import *

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class RobotCreatingWindow(QDialog):
    def __init__(self, mainUi):
        super(RobotCreatingWindow, self).__init__()
        uic.loadUi('uiFiles/robotList.ui', self)

        self.mainUi = mainUi

        self.submitButton.clicked.connect(self.submit)
        self.prepareRobotList()

    def prepareRobotList(self):
        self.robotComboBox.addItems(getCreatedRobots())

    def submit(self):
        newRobot = self.mainUi.robotTree.selectedItems()[0]
        selectedRobot = self.robotComboBox.currentText()
        newRobot.setText(0, selectedRobot)
        self.mainUi.updateController()
        self.close()
