import dataclasses
import json

from utils.constants import *
from utils.guiMethods import *
from utils.templates import *

from classes.serializer import PlayerParams, TeamParams, Game
from classes.player import Player

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QWidget, QTreeWidget, QPushButton, QAction, QTreeWidgetItem, QComboBox

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('uiFiles/gui.ui', self)

        self.addContextMenus()

        self.teamTree = self.findChild(QTreeWidget, 'teamTree')  # list of teams
        self.teamTree.itemClicked.connect(self.teamTreeItemClickTrigger)

        self.playerTree = self.findChild(QTreeWidget, 'playerTree')  # list of players
        self.playerTree.itemClicked.connect(self.playerTreeItemClickTrigger)

        self.createJsonButton = self.findChild(QPushButton, 'createJsonButton')
        self.createJsonButton.clicked.connect(self.createJson)

        self.test = QPushButton()
        self.currentTeamIndex = 0

    def addContextMenus(self):
        self.teamTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.teamTree.customContextMenuRequested.connect(self.showTeamTreeContextMenu)

        self.playerTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.playerTree.customContextMenuRequested.connect(self.showPlayerTreeContextMenu)

    def showTeamTreeContextMenu(self, position):
        menu, action = callTreeContextMenu('Create new team', self.playerTree)
        action.triggered.connect(self.createNewTeam)
        menu.exec_(self.teamTree.mapToGlobal(position))

    def showPlayerTreeContextMenu(self, position):
        menu, action = callTreeContextMenu('Create new player', self.playerTree)
        action.triggered.connect(self.createNewPlayer)
        menu.exec_(self.playerTree.mapToGlobal(position))

    def createNewTeam(self):
        newTeam = QTreeWidgetItem()

        color = QTreeWidgetItem()
        color.setText(0, 'Color')
        name = QTreeWidgetItem()
        name.setText(0, 'Name')

        newTeam.addChildren([color, name])
        newTeam.setText(0, 'New team')

        self.teamTree.addTopLevelItems([newTeam])
        teamList.append(newTeam)
        playerList.append([])

    def createNewPlayer(self):
        newPlayer = QTreeWidgetItem()

        controlObject = QComboBox()
        controlObject.setMaximumWidth(self.width() // 8)
        controlObject.addItems(CONTROL_OBJECTS)
        controlObjectItem = QTreeWidgetItem()
        controlObjectItem.setText(0, 'ControlObject')
        newPlayer.addChild(controlObjectItem)
        self.playerTree.setItemWidget(controlObjectItem, 1, controlObject)

        ipItem = QTreeWidgetItem()
        ipItem.setText(0, 'Ip')
        newPlayer.addChild(ipItem)

        portItem = QTreeWidgetItem()
        portItem.setText(0, 'Port')
        newPlayer.addChild(portItem)

        roleObject = QComboBox()
        roleObject.setMaximumWidth(self.width() // 6)
        roleObject.addItems(ROLES)
        roleObjectItem = QTreeWidgetItem()
        roleObjectItem.setText(0, 'Role object')
        newPlayer.addChild(roleObjectItem)
        self.playerTree.setItemWidget(roleObjectItem, 1, roleObject)

        nameItem = QTreeWidgetItem()
        nameItem.setText(0, 'Player name')
        newPlayer.addChild(nameItem)

        newPlayer.setText(0, 'New player')

        self.playerTree.addTopLevelItems([newPlayer])
        playerList[self.currentTeamIndex].append(newPlayer)

    def teamTreeItemClickTrigger(self, item, col):
        self.hideAllChildren(playerList[self.currentTeamIndex])
        self.currentTeamIndex = self.teamTree.indexOfTopLevelItem(item)
        self.showAllChildren(playerList[self.currentTeamIndex])

        # Flags to allow object fields editing
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def playerTreeItemClickTrigger(self, item, col):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def createJson(self):
        game = Game([])

        for i in range(self.teamTree.invisibleRootItem().childCount()):
            root = self.teamTree.invisibleRootItem()

            name_team = root.child(i).text(1)
            players = []

            try:
                color_team = list(map(int, self.teamTree.invisibleRootItem().child(i).child(0).text(1).split(',')))
            except ValueError:  # if color string is empty
                color_team = [0, 0, 0]

            for player in playerList[i]:
                if player:
                    control_obj = self.playerTree.itemWidget(player.child(0), 1).currentText()
                    ip = player.child(1).text(1)
                    port = player.child(2).text(1)
                    role_obj = self.playerTree.itemWidget(player.child(3), 1).currentText()
                    name_player = player.child(4).text(1)

                    playerParams = PlayerParams(name_player=name_player,
                                                control_obj=control_obj,
                                                role_obj=role_obj,
                                                method_control_obj="",
                                                ip=ip,
                                                port=port)
                    players.append(playerParams)

            teamParams = TeamParams(players=players,
                                    name_team=name_team,
                                    color_team=color_team)
            game.teams.append(teamParams)

        with open('config.json', 'w') as output_file:
            output_file.write(json.dumps(dataclasses.asdict(game), indent=2))

    @staticmethod
    def hideAllChildren(children):
        for child in children:
            child.setHidden(True)

    @staticmethod
    def showAllChildren(children):
        for child in children:
            child.setHidden(False)

    # def fillItemLists(self):
    #     for i in range(self.teamTree.invisibleRootItem().childCount()):
    #         teamList.append(self.teamTree.invisibleRootItem().child(i))
    #     for i in range(self.playerTree.invisibleRootItem().childCount()):
    #         playerList.append(self.playerTree.invisibleRootItem().child(i))
