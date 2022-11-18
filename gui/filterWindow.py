from utils.templates import *

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton, QTreeWidget, QTreeWidgetItem


class FilterWindow(QWidget):
    def __init__(self, mainUi, object_filter):
        super(FilterWindow, self).__init__()
        uic.loadUi('uiFiles/filter.ui', self)

        self.mainUi = mainUi
        self.object_filter = object_filter

        self.dObjectTree = self.findChild(QTreeWidget, 'dObjectTree')

        self.filterSelectButton = self.findChild(QPushButton, 'filterSelectButton')
        self.filterSelectButton.clicked.connect(self.selectButtonClicked)

        self.preparePlayerList()

    def preparePlayerList(self):
        teamRoot = self.mainUi.teamTree.invisibleRootItem()
        teamCount = 0

        for strTeam in itemListToStr([teamRoot.child(i) for i in range(teamRoot.childCount())]):
            newTeamWidget = QTreeWidgetItem()
            newTeamWidget.setText(0, strTeam)

            for player in playerList[teamCount]:
                newPlayerWidget = QTreeWidgetItem()
                newPlayerWidget.setText(0, player.text(0))
                newTeamWidget.addChild(newPlayerWidget)

            teamCount += 1

            self.dObjectTree.addTopLevelItems([newTeamWidget])

    def selectButtonClicked(self):
        child = self.dObjectTree.selectedItems()[0]
        parent = child.parent()
        if child.childCount() == 0:
            team_ind = self.dObjectTree.indexOfTopLevelItem(parent)
            player_ind = parent.indexOfChild(child)
            self.close()

            currFilter = self.object_filter.text(1)

            # Don't do anything if playing has already selected
            if f'{team_ind}, {player_ind}' in self.object_filter.text(1):
                return

            if currFilter == '':
                self.object_filter.setText(1, f'{team_ind}, {player_ind}')
            else:
                self.object_filter.setText(1, f'{self.object_filter.text(1)} ; {team_ind}, {player_ind}')
