import dataclasses
import json
import re

from classes.dataclasses import ObjectParams
from utils.constants import *
from utils.templates import *

from classes.dataclasses import *

from gui.filterWindow import FilterWindow
from gui.robotWindow import RobotWindow

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QTreeWidget, QPushButton, QTreeWidgetItem, QComboBox, QFontComboBox, QFileDialog

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('uiFiles/gui.ui', self)

        # Tree widgets
        self.robotTree = self.findChild(QTreeWidget, 'robotTree_2')
        self.robotTree.itemClicked.connect(self.robotTreeItemClickTrigger)

        self.teamTree = self.findChild(QTreeWidget, 'teamTree_2')  # list of teams
        self.teamTree.itemClicked.connect(self.teamTreeItemClickTrigger)

        self.playerTree = self.findChild(QTreeWidget, 'playerTree_2')  # list of players
        self.playerTree.itemDoubleClicked.connect(self.playerTreeDoubleClickTrigger)
        self.playerTree.itemClicked.connect(self.playerTreeItemClickTrigger)

        self.objectTree = self.findChild(QTreeWidget, 'objectTree_2')
        self.objectTree.itemDoubleClicked.connect(self.objectTreeDoubleClickTrigger)
        self.objectTree.itemClicked.connect(self.objectTreeItemClickTrigger)

        # Buttons
        self.createPolygonJsonButton = self.findChild(QPushButton, 'createPolygonJsonButton')
        self.createPolygonJsonButton.clicked.connect(self.createPolygonJSON)

        self.loadPolygonJsonButton = self.findChild(QPushButton, 'loadPolygonJsonButton')
        self.loadPolygonJsonButton.clicked.connect(self.loadPolygonJSON)

        self.createRobotJsonButton = self.findChild(QPushButton, 'createRobotJsonButton')
        self.createRobotJsonButton.clicked.connect(self.createRobotJSON)

        self.loadRobotJsonButton = self.findChild(QPushButton, 'loadRobotJsonBtn')
        self.loadRobotJsonButton.clicked.connect(self.loadRobotJSON)

        self.createTeamJsonButton = self.findChild(QPushButton, 'createTeamJsonButton')
        self.createTeamJsonButton.clicked.connect(self.createTeamJSON)

        self.loadTeamJsonButton = self.findChild(QPushButton, 'loadTeamJsonButton')
        self.loadTeamJsonButton.clicked.connect(self.loadTeamJSON)

        self.currentTeamIndex = 0

        # flags for item removing
        self.isRobotSelected = False
        self.isTeamSelected = False
        self.isPlayerSelected = False
        self.isObjectSelected = False

        self.addContextMenus()

    def addContextMenus(self):
        self.robotTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.robotTree.customContextMenuRequested.connect(self.showRobotTreeContextMenu)

        self.teamTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.teamTree.customContextMenuRequested.connect(self.showTeamTreeContextMenu)

        self.playerTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.playerTree.customContextMenuRequested.connect(self.showPlayerTreeContextMenu)

        self.objectTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.objectTree.customContextMenuRequested.connect(self.objectTreeContextMenu)

    def showRobotTreeContextMenu(self, position):
        menu, createAction, removeAction = callTreeContextMenu('Create new robot', 'Remove robot', self.robotTree,
                                                               self.isRobotSelected)
        createAction.triggered.connect(self.createNewRobot)
        removeAction.triggered.connect(self.removeRobot) if self.isRobotSelected else None
        menu.exec_(self.robotTree.mapToGlobal(position))

    def showTeamTreeContextMenu(self, position):
        menu, createAction, removeAction = callTreeContextMenu('Create new team', 'Remove team', self.playerTree,
                                                               self.isTeamSelected)
        createAction.triggered.connect(self.createNewTeam)
        removeAction.triggered.connect(self.removeTeam) if self.isTeamSelected else None
        menu.exec_(self.teamTree.mapToGlobal(position))

    def showPlayerTreeContextMenu(self, position):
        # callTreeContextMenu method allows removing player if player is selected
        menu, createAction, removeAction = callTreeContextMenu('Create new player', 'Remove player', self.playerTree,
                                                               self.isPlayerSelected)
        createAction.triggered.connect(self.createNewPlayer)
        removeAction.triggered.connect(self.removePlayer) if self.isPlayerSelected else None
        menu.exec_(self.playerTree.mapToGlobal(position))

    def objectTreeContextMenu(self, position):
        menu, createAction, removeAction = callTreeContextMenu('Create new object', 'Remove object', self.objectTree,
                                                               self.isObjectSelected)
        createAction.triggered.connect(self.createNewObject)
        removeAction.triggered.connect(self.removeObject) if self.isObjectSelected else None
        menu.exec_(self.objectTree.mapToGlobal(position))

    # Creating methods
    def createNewRobot(self):
        newRobot = QTreeWidgetItem()
        defaultRobot = RobotParams()

        for field in list(RobotParams.__annotations__.keys())[1:]:
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultRobot.__dict__.get(field)))
            newRobot.addChild(newFieldItem)

            if field in ROBOT_CUSTOM_FIELDS:
                self.robotTree.setItemWidget(newFieldItem, 1, createComboBoxSubwidget(self.width() // 5,
                                                                                      RobotParams.aliases.get(field)))

        newRobot.setText(0, 'New robot')
        self.robotTree.addTopLevelItems([newRobot])

    def createNewTeam(self):
        newTeam = QTreeWidgetItem()
        defaultTeam = TeamParams([])

        for field in list(TeamParams.__annotations__.keys())[2:]:  # start from 2 cuz 0 is player list, 1 is title
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultTeam.__dict__.get(field)))
            newTeam.addChild(newFieldItem)

        newTeam.setText(0, 'New team')

        self.teamTree.addTopLevelItems([newTeam])
        teamList.append(newTeam)
        playerList.append([])

    def createNewPlayer(self):
        if not self.teamTree.invisibleRootItem().childCount():
            return

        newPlayer = QTreeWidgetItem()
        defaultPlayer = PlayerParams()  # object for parsing default params

        for field in list(PlayerParams.__annotations__.keys())[1:]:
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultPlayer.__dict__.get(field)))
            newPlayer.addChild(newFieldItem)

            if field in PLAYER_CUSTOM_FIELDS:
                self.playerTree.setItemWidget(newFieldItem, 1, createComboBoxSubwidget(self.width() // 5,
                                                                                       PlayerParams.aliases.get(field)))

        newPlayer.setText(0, 'New player')

        self.playerTree.addTopLevelItems([newPlayer])

        playerList[self.currentTeamIndex].append(newPlayer)

    def createNewObject(self):
        newObject = QTreeWidgetItem()
        defaultObject = ObjectParams()

        for field in list(ObjectParams.__annotations__.keys())[1:]:
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultObject.__dict__.get(field)))
            newObject.addChild(newFieldItem)

        newObject.setText(0, 'New object')

        self.objectTree.addTopLevelItems([newObject])

    # Removing methods
    def removeRobot(self):
        root = self.robotTree.invisibleRootItem()
        for item in self.robotTree.selectedItems():
            (item.parent() or root).removeChild(item)
        self.isRobotSelected = False

    def removeTeam(self):
        root = self.teamTree.invisibleRootItem()
        for item in self.teamTree.selectedItems():
            # removing items from gui
            (item.parent() or root).removeChild(item)

            self.currentTeamIndex = self.teamTree.indexOfTopLevelItem(item)
            for player in playerList[self.currentTeamIndex]:
                playerRoot = self.playerTree.invisibleRootItem()
                (player.parent() or playerRoot).removeChild(player)

            # removing items from background lists
            del teamList[self.currentTeamIndex]
            del playerList[self.currentTeamIndex]

            self.currentTeamIndex = 0

        self.isTeamSelected = False

        try:
            self.teamTree.invisibleRootItem().child(0).setSelected(False)
        except AttributeError:  # if last item was removed
            pass

    def removePlayer(self):
        root = self.playerTree.invisibleRootItem()
        for item in self.playerTree.selectedItems():
            (item.parent() or root).removeChild(item)
        self.isPlayerSelected = False

    def removeObject(self):
        root = self.objectTree.invisibleRootItem()
        for item in self.objectTree.selectedItems():
            (item.parent() or root).removeChild(item)
        self.isObjectSelected = False

    # Triggers
    def robotTreeItemClickTrigger(self, item, col):
        self.isRobotSelected = True
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def teamTreeItemClickTrigger(self, item, col):
        self.isTeamSelected = True

        self.hideAllChildren(playerList[self.currentTeamIndex])
        self.currentTeamIndex = self.teamTree.indexOfTopLevelItem(item)
        self.showAllChildren(playerList[self.currentTeamIndex])

        # Flags to allow object fields editing
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def playerTreeItemClickTrigger(self, item, col):
        self.isPlayerSelected = True

        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def playerTreeDoubleClickTrigger(self, item, col):
        if item.text(0) == 'robot':
            self.robotWindow = RobotWindow(self, item)
            self.robotWindow.show()

    def objectTreeItemClickTrigger(self, item, col):
        self.isObjectSelected = True

        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def objectTreeDoubleClickTrigger(self, item, col):
        if item.text(0) == 'filter':
            self.filterWindow = FilterWindow(self, item)
            self.filterWindow.show()

    def createPolygonJSON(self):
        polygonParams = PolygonParams([])
        root = self.objectTree.invisibleRootItem()
        objectList = [root.child(i) for i in range(root.childCount())]

        for obj in objectList:
            dataclassPolygonObject = dataclassFromWidget(obj, ObjectParams(), self.objectTree)
            polygonParams.objects.append(dataclassPolygonObject)

        saveToFile('polygon.json', json.dumps(dataclasses.asdict(polygonParams), indent=2))

    def createRobotJSON(self):
        robotDataclass = Robots([])
        root = self.robotTree.invisibleRootItem()
        objectList = [root.child(i) for i in range(root.childCount())]

        for obj in objectList:
            dataclassRobotFromWidget = dataclassFromWidget(obj, RobotParams(), self.robotTree)
            robotDataclass.robotList.append(dataclassRobotFromWidget)

        saveToFile('robots.json', json.dumps(dataclasses.asdict(robotDataclass), indent=2))

    def createTeamJSON(self):
        gameDataclass = Game([])

        root = self.teamTree.invisibleRootItem()

        for i in range(root.childCount()):
            teamWidget = root.child(i)
            teamDataclass = dataclassFromWidget(teamWidget, TeamParams([]), self.teamTree)

            for player in playerList[i]:
                playerDataClass = dataclassFromWidget(player, PlayerParams(), self.playerTree)
                teamDataclass.players.append(playerDataClass)

            gameDataclass.teams.append(teamDataclass)

        saveToFile('players.json', json.dumps(dataclasses.asdict(gameDataclass), indent=2))

    def loadPolygonJSON(self):
        filepath = getSelectedJson(self, 'Select file')
        polygon = PolygonParams(**readJSON(filepath))
        polygon.objects = serializeChildren(polygon.objects, ObjectParams)
        fillObjectTree(polygon, self.objectTree)

    def loadRobotJSON(self):
        filepath = getSelectedJson(self, 'Select file')
        robots = Robots(**readJSON(filepath))
        robots.robotList = serializeChildren(robots.robotList, RobotParams)
        fillRobotTree(robots, self.robotTree)

    def loadTeamJSON(self):
        self.clearGameData()

        filepath = getSelectedJson(self, 'Select file')

        game = Game(**readJSON(filepath))
        game.teams = serializeChildren(game.teams, TeamParams)

        for team in game.teams:
            team.players = serializeChildren(team.players, PlayerParams)

        fillGameTree(game, self.teamTree, self.playerTree)

    def hideAllChildren(self, children):
        self.isPlayerSelected = False  # Don't allow removing players if player is hidden
        for child in children:
            child.setHidden(True)

    def clearGameData(self):
        self.teamTree.clear()
        self.playerTree.clear()
        teamList.clear()
        playerList.clear()

    @staticmethod
    def showAllChildren(children):
        for child in children:
            child.setHidden(False)
