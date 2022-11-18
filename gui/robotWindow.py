from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem


class RobotWindow(QWidget):
    def __init__(self, mainUi, robotWidget):
        super(RobotWindow, self).__init__()
        uic.loadUi('uiFiles/robot.ui', self)

        self.mainUi = mainUi
        self.robotWidget = robotWidget

        self.dRobotTree = self.findChild(QTreeWidget, 'dRobotTree')

        self.robotSelectButton = self.findChild(QPushButton, 'robotSelectButton')
        self.robotSelectButton.clicked.connect(self.robotSelectButtonClicked)

        self.prepareRobotList()

    def prepareRobotList(self):
        robotRoot = self.mainUi.robotTree.invisibleRootItem()

        for robot in [robotRoot.child(i) for i in range(robotRoot.childCount())]:
            newTeamWidget = QTreeWidgetItem()
            newTeamWidget.setText(0, robot.text(0))
            self.dRobotTree.addTopLevelItems([newTeamWidget])

    def robotSelectButtonClicked(self):
        selectedRobot = self.dRobotTree.selectedItems()[0]
        index = self.dRobotTree.indexOfTopLevelItem(selectedRobot)
        self.robotWidget.setText(1, f'{index}')
        self.close()
