import configparser
import json

import numpy as np

from utils.templates import *
from utils.localization import *

from classes.dataclasses import *

from gui.filterWindow import FilterWindow
from gui.robotWindow import RobotWindow

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.image import imread
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QTreeWidget, QPushButton, QTreeWidgetItem, QTabWidget, QGraphicsView, QGraphicsScene, \
    QGraphicsItem, QMessageBox, QLabel, QLineEdit

import requests

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QtWidgets.QMainWindow):
    """
    The main class for this application.
    OnInit() method contains all child elements.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('uiFiles/gui.ui', self)
        self.onInit()

    def onInit(self):
        # localization
        self.currentLocale = 'EN'
        self.config = configparser.ConfigParser()
        self.config.read(f'locales/{self.currentLocale}.ini', encoding='utf-8')

        #  Menu action
        self.actionRussian = self.findChild(QAction, 'actionRussian')
        self.actionRussian.triggered.connect(self.translateToRUS)

        self.actionEnglish = self.findChild(QAction, 'actionEnglish')
        self.actionEnglish.triggered.connect(self.translateToEN)

        # Tree widgets
        self.robotTree = self.findChild(QTreeWidget, 'robotTree')
        self.robotTree.itemClicked.connect(self.robotTreeItemClickTrigger)

        self.teamTree = self.findChild(QTreeWidget, 'teamTree')  # list of teams
        self.teamTree.itemClicked.connect(self.teamTreeItemClickTrigger)

        self.playerTree = self.findChild(QTreeWidget, 'playerTree')  # list of players
        self.playerTree.itemDoubleClicked.connect(self.playerTreeDoubleClickTrigger)
        self.playerTree.itemClicked.connect(self.playerTreeItemClickTrigger)

        self.objectTree = self.findChild(QTreeWidget, 'objectTree')
        self.objectTree.itemDoubleClicked.connect(self.objectTreeDoubleClickTrigger)
        self.objectTree.itemClicked.connect(self.objectTreeItemClickTrigger)

        # Buttons
        self.createPolygonJsonButton.clicked.connect(self.createPolygonJSON)
        self.loadPolygonJsonButton.clicked.connect(self.loadPolygonJSON)
        self.createRobotJsonButton.clicked.connect(self.createRobotJSON)
        self.loadRobotJsonButton.clicked.connect(self.loadRobotJSON)
        self.createTeamJsonButton.clicked.connect(self.createTeamJSON)
        self.loadTeamJsonButton.clicked.connect(self.loadTeamJSON)

        self.sendJsonButton.clicked.connect(self.sendJson)
        self.createGameButton.clicked.connect(self.createGame)
        self.startGameButton.clicked.connect(self.startGame)
        self.restartGameButton.clicked.connect(self.restartGame)
        self.stopGameButton.clicked.connect(self.stopGame)

        # ComboBoxes
        self.jsonSelectingComboBox.currentIndexChanged.connect(self.sendJson)

        # LineEdits
        self.hostnameLineEdit.textChanged.connect(self.updateServerAddress)
        self.portLineEdit.textChanged.connect(self.updateServerAddress)

        # Graphics
        self.graphicsView = self.findChild(QGraphicsView, 'graphicsView')
        self.graphicsScene = QGraphicsScene()
        self.graphicsView.setScene(self.graphicsScene)

        # Client-server
        self.serverAddr = ''
        self.session = requests.session()

        # flags for item removing
        self.isRobotSelected = False
        self.isTeamSelected = False
        self.isPlayerSelected = False
        self.isObjectSelected = False

        # flags for file selecting
        self.isPolygonJsonSelected = False
        self.isRobotsJsonSelected = False
        self.isTeamsJsonSelected = False

        # flags for game preparing
        self.isReadyToCreate = False

        # timers for plots
        self.plotTimer = QtCore.QTimer()
        self.plotTimer.setInterval(500)
        self.plotTimer.timeout.connect(self.updatePlots)
        # self.plotTimer.start()

        self.stateTimer = QtCore.QTimer()
        self.stateTimer.setInterval(1000)
        self.stateTimer.timeout.connect(self.updateState)
        # self.stateTimer.start()

        # Other variables
        self.filesSent = []
        self.currentTeamIndex = 0

        self.addContextMenus()
        self.translateToEN()

    def updatePlots(self):
        self.graphicsScene.clear()

        if self.externalTab.currentIndex() != 2:  # Do not do anything if the visualizing tab is hidden
            return

        matplotlib.use("Qt5agg")
        data = self.session.get('http://127.0.0.1:5000/update').json().get('ans')  # Get position of robots

        # Set up plots
        img = imread('images/robot.png')
        fig, ax = plt.subplots()
        plt.ylim([-10, 110])
        plt.xlim([-10, 110])
        plt.grid(True)

        # Plot
        for i in range(len(data)):
            imgBox = OffsetImage(img, zoom=0.5)
            ab = AnnotationBbox(imgBox, (data[i][0], data[i][1]), frameon=False)
            ax.add_artist(ab)

        canvas = FigureCanvas(fig)
        plt.close()  # Close for optimization
        self.graphicsScene.addWidget(canvas)

    def updateState(self):
        if self.externalTab.currentIndex() != 1:
            return

        data = self.session.get(f'{self.serverAddr}/server_control').json()
        updateStateTable(objectFromDict(data, ServerState), self.infoTable)

        data = self.session.get(f'{self.serverAddr}/data_player').json()
        updateStateTable(objectFromDict(data, Command), self.commandTable)

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

    def updateServerAddress(self):
        self.serverAddr = f"http://{self.hostnameLineEdit.text()}:{self.portLineEdit.text()}/"

    # Button controllers
    def createPolygonJSON(self):
        polygonParams = PolygonParams([])
        root = self.objectTree.invisibleRootItem()
        objectList = [root.child(i) for i in range(root.childCount())]

        for obj in objectList:
            dataclassPolygonObject = dataclassFromWidget(obj, ObjectParams(), self.objectTree)
            polygonParams.objects.append(dataclassPolygonObject)

        saveToFile('json/polygon.json', json.dumps(dataclasses.asdict(polygonParams), indent=2))

    def createRobotJSON(self):
        robotDataclass = Robots([])
        root = self.robotTree.invisibleRootItem()
        objectList = [root.child(i) for i in range(root.childCount())]

        for obj in objectList:
            dataclassRobotFromWidget = dataclassFromWidget(obj, RobotParams(), self.robotTree)
            robotDataclass.robotList.append(dataclassRobotFromWidget)

        saveToFile('json/robots.json', json.dumps(dataclasses.asdict(robotDataclass), indent=2))

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

        saveToFile('json/players.json', json.dumps(dataclasses.asdict(gameDataclass), indent=2))

    def loadPolygonJSON(self):
        """Loads Polygon's dataclass from the JSON file"""
        self.clearPolygonData()
        filepath = getSelectedJson(self, 'Select file')

        try:
            polygon = PolygonParams(**readJSON(filepath))
            polygon.objects = serializeChildren(polygon.objects, ObjectParams)
            fillObjectTree(polygon, self.objectTree)
            self.polygonLabel.setText(f"{self.config.get('LOCALE', 'jsonLabel')} {filepath.split('/')[-1]}")
            self.isPolygonJsonSelected = True
        except TypeError:  # if file selecting was cancelled
            pass

    def loadRobotJSON(self):
        """Loads robot dataclass from the JSON file"""
        self.clearRobotData()
        filepath = getSelectedJson(self, 'Select file')

        try:
            robots = Robots(**readJSON(filepath))
            robots.robotList = serializeChildren(robots.robotList, RobotParams)
            fillRobotTree(robots, self.robotTree)
            self.robotsLabel.setText(f"{self.config.get('LOCALE', 'jsonLabel')} {filepath.split('/')[-1]}")
            self.isRobotsJsonSelected = True
        except TypeError:
            pass

    def loadTeamJSON(self):
        """Loads team's dataclass from the JSON file"""
        self.clearTeamData()
        filepath = getSelectedJson(self, 'Select file')

        try:
            game = Game(**readJSON(filepath))
            game.teams = serializeChildren(game.teams, TeamParams)

            for team in game.teams:
                team.players = serializeChildren(team.players, PlayerParams)

            fillGameTree(game, self.teamTree, self.playerTree)
            self.teamsLabel.setText(f"{self.config.get('LOCALE', 'jsonLabel')} {filepath.split('/')[-1]}")
            self.isTeamsJsonSelected = True
        except TypeError:
            pass

    def sendJson(self):
        """
        Sends JSON file(-s) to the http server.

        If you want to send tab's json file, make sure that it was loaded and still in the directory.
        """

        # 0 index is polygon
        # 1 index is robots
        # 2 index is teams & players
        # 3 index is all
        currIndex = self.jsonSelectingComboBox.currentIndex()

        try:
            if (currIndex == 0) and self.isPolygonJsonSelected:
                data = open("json/polygon.json").read()

                try:
                    self.session.get(f"{self.serverAddr}", params=dict(target="set",
                                                                       type_command="core",
                                                                       command="save_json",
                                                                       filename='polygon.json'), json=data)
                except requests.exceptions.MissingSchema or ConnectionError:
                    self.showWarning(self.config.get("LOCALE", "hostError"))

            elif (currIndex == 1) and self.isRobotsJsonSelected:
                data = open("json/robots.json").read()

                try:
                    self.session.get(f"{self.serverAddr}", params=dict(target="set",
                                                                       type_command="core",
                                                                       command="save_json",
                                                                       filename='robots.json'), json=data)
                except requests.exceptions.MissingSchema or ConnectionError:
                    self.showWarning(self.config.get("LOCALE", "hostError"))

            elif (currIndex == 2) and self.isTeamsJsonSelected:
                data = open("json/players.json").read()

                try:
                    self.session.get(f"{self.serverAddr}", params=dict(target="set",
                                                                       type_command="core",
                                                                       command="save_json",
                                                                       filename='players'), json=data)
                except requests.exceptions.MissingSchema or ConnectionError:
                    self.showWarning(self.config.get("LOCALE", "hostError"))

            else:
                files = getMultipleSelectedJson(self)

                trashFlag = False  # will be set to True if not json

                for file in files:
                    filename = file.split('/')[-1].split('.')[0]
                    filetype = file.split('/')[-1].split('.')[1]

                    self.filesSent.append(filename) if filename not in self.filesSent else None

                    if filetype != 'json':
                        trashFlag = True
                        continue

                    data = open(file).read()

                    try:
                        self.session.get(f"{self.serverAddr}", params=dict(target="set",
                                                                           type_command="core",
                                                                           command=f"save_json",
                                                                           filename=filename), json=data)
                        self.statusLabel.setText(self.config.get('LOCALE', 'successfully'))
                    except requests.exceptions.MissingSchema or ConnectionError:
                        self.isReadyToCreate = False
                        self.statusLabel.setText(self.config.get('LOCALE', 'error'))
                        self.showWarning(self.config.get("LOCALE", "hostError"))
                        return

                if trashFlag:  # Show error message if file extension != json
                    self.showWarning(self.config.get("LOCALE", "wrongExtension"))
                    return

                self.isReadyToCreate = True

        except FileNotFoundError or TypeError:
            self.showWarning(self.config.get("LOCALE", "fileNotFound"))

    def createGame(self):
        """Sends game create request"""
        if (len(self.filesSent) < 3) or not self.isReadyToCreate:
            self.showWarning(self.config.get('LOCALE', 'notEnoughFiles'))
            return

        try:
            data = self.session.get(f'{self.serverAddr}', params=dict(target="set",
                                                                      type_command="core",
                                                                      command="create_game",
                                                                      param=None)).json().get('data')

            self.statusLabel.setText(self.config.get('LOCALE', 'successfully'))

            updateStateTable(objectFromDict(json.loads(data), ServerState), self.infoTable)

            playerId = 0
            for team in teamList:
                currTeamIdx = teamList.index(team)

                for player in playerList[currTeamIdx]:
                    playerItem = PlayerItemFromPlayerWidget(player, playerId, team.text(0))
                    playerId += 1

                    updateStateTable(playerItem, self.commandTable)

        except requests.exceptions.MissingSchema or ConnectionError:
            self.showWarning(self.config.get('LOCALE', 'hostError'))

    def startGame(self):
        """Sends game start request"""
        try:
            self.session.get(f'{self.serverAddr}', params=dict(target="set",
                                                               type_command="core",
                                                               command="start_game",
                                                               param=self.delayComboBox.currentText().split()[-1]))
        except requests.exceptions.MissingSchema or ConnectionError:
            self.showWarning(self.config.get('LOCALE', 'hostError'))

    def restartGame(self):
        """Sends game restart request"""
        try:
            self.session.get(f'{self.serverAddr}', params=dict(target="set",
                                                               type_command="core",
                                                               command="restart_game",
                                                               param=None))
        except requests.exceptions.MissingSchema or ConnectionError:
            self.showWarning(self.config.get('LOCALE', 'hostError'))

    def stopGame(self):
        """Sends game stop request"""
        try:
            self.session.get(f'{self.serverAddr}', params=dict(target="set",
                                                               type_command="core",
                                                               command="stop_game",
                                                               param=None))
        except requests.exceptions.MissingSchema or ConnectionError:
            self.showWarning(self.config.get('LOCALE', 'hostError'))

    def hideAllChildren(self, children):
        self.isPlayerSelected = False  # Don't allow removing players if player is hidden
        for child in children:
            child.setHidden(True)

    def clearPolygonData(self):
        self.objectTree.clear()
        self.isObjectSelected = False

    def clearRobotData(self):
        self.robotTree.clear()
        self.isRobotSelected = False

    def clearTeamData(self):
        self.teamTree.clear()
        self.playerTree.clear()
        teamList.clear()
        playerList.clear()

        self.isTeamSelected = False
        self.isPlayerSelected = False

    def translateToRUS(self):
        self.currentLocale = 'RU'
        translateToRUS(self, 0)

    def translateToEN(self):
        self.currentLocale = 'EN'
        translateToEN(self, 0)

    def showWarning(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    @staticmethod
    def showAllChildren(children):
        for child in children:
            child.setHidden(False)
