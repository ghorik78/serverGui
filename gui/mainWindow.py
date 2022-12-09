import configparser
import dataclasses
import json

from database.database import *

from utils.templates import *
from utils.localization import *

from classes.dataclasses import *

from gui.robotCreatingWindow import RobotCreatingWindow
from gui.playerRoleWindow import PlayerRoleWindow
from gui.polygonRoleWindow import PolygonRoleWindow
from gui.filterWindow import FilterWindow
from gui.robotWindow import RobotWindow
from gui.socketSettingsWindow import SocketSettingsWindow

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.image import imread, imsave
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from scipy import ndimage

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
        """
        This method will initialize all mainWindow children.
        EN locale will be set as default.
        """
        # localization
        self.currentLocale = 'EN'
        self.config = configparser.ConfigParser()
        self.config.read(f'locales/{self.currentLocale}.ini', encoding='utf-8')

        # Roles
        self.objectRolesDict = createObjectRolesDict(self.currentLocale)
        self.playerRolesDict = createPlayerRolesDict(self.currentLocale)

        # Menu action
        self.actionRussian.triggered.connect(self.translateToRU)
        self.actionEnglish.triggered.connect(self.translateToEN)

        self.saveAsAct.triggered.connect(self.saveAs)
        self.saveGameAct.triggered.connect(self.exportGameJSON)
        self.openCfgAct.triggered.connect(self.importJSON)
        self.openGameCfgAct.triggered.connect(self.importGameJSON)

        self.actionSocketSettings.triggered.connect(self.changeSocketSettings)

        # Tree widgets
        self.objectTree.itemChanged.connect(self.posChanged)
        self.robotTree.itemClicked.connect(self.robotTreeItemClickTrigger)
        self.teamTree.itemClicked.connect(self.teamTreeItemClickTrigger)
        self.playerTree.itemDoubleClicked.connect(self.playerTreeDoubleClickTrigger)
        self.playerTree.itemClicked.connect(self.playerTreeItemClickTrigger)
        self.objectTree.itemDoubleClicked.connect(self.objectTreeDoubleClickTrigger)
        self.objectTree.itemClicked.connect(self.objectTreeItemClickTrigger)

        # Buttons
        self.createPolygonObjBttn.clicked.connect(self.createNewObject)
        self.removeSelectedObjBttn.clicked.connect(self.removeObject)
        self.removeAllObjBttn.clicked.connect(self.removeAllObjects)

        self.createRobotBttn.clicked.connect(self.createNewRobot)
        self.removeSelectedRobotsBttn.clicked.connect(self.removeRobot)
        self.removeAllRobotsBttn.clicked.connect(self.removeAllRobots)

        self.createTeamBttn.clicked.connect(self.createNewTeam)
        self.removeSelectedTeamBttn.clicked.connect(self.removeTeam)
        self.removeAllTeamsBttn.clicked.connect(self.removeAllTeams)

        self.createPlayerBttn.clicked.connect(self.createNewPlayer)
        self.removeSelectedPlayerBttn.clicked.connect(self.removePlayer)
        self.removeAllPlayersBttn.clicked.connect(self.removeAllPlayers)

        self.createGameBttn.clicked.connect(self.createGame)
        self.startGameButton.clicked.connect(self.startGame)
        self.restartGameButton.clicked.connect(self.restartGame)
        self.stopGameButton.clicked.connect(self.stopGame)

        # ComboBoxes

        # Graphics
        self.objectsCoords = [[0.0, 0.0]]
        self.minX, self.maxX = 0.0, 0.0
        self.minY, self.maxY = 0.0, 0.0

        self.graphicsView = self.findChild(QGraphicsView, 'graphicsView')
        self.graphicsScene = QGraphicsScene()
        self.graphicsView.setScene(self.graphicsScene)

        self.polygonGraphicsScene = QGraphicsScene()
        self.polygonGraphicsView.setScene(self.polygonGraphicsScene)

        # Client-server
        self.hostname = ''
        self.port = ''
        self.serverAddr = ''
        self.session = requests.session()

        # Vars for indexing
        self.totalCreated = dict()

        # flags for item removing
        self.isRobotSelected = False
        self.isTeamSelected = False
        self.isPlayerSelected = False
        self.isObjectSelected = False

        # flags for file selecting
        self.isPolygonJsonSelected = False
        self.isRobotsJsonSelected = False
        self.isTeamsJsonSelected = False

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

        self.translateToEN()
        self.addContextMenus()
        self.updateController()

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

    def updatePolygonPlots(self):
        """
        Redraws all objects in the first tab.
        :return: None
        """
        self.polygonGraphicsScene.clear()

        fig, ax = plt.subplots()
        fig.set_figheight(4.25)
        fig.set_figwidth(4.25)
        ax.set_aspect(1)

        root = self.objectTree.invisibleRootItem()
        children = [root.child(i) for i in range(root.childCount())]

        try:
            for child in children:
                role = removeDigitsFromStr(child.text(0))
                position = listFromStr(child.child(getFieldIndex(child, 'position')).text(1))
                ax.add_artist(createFigureByRole(self.currentLocale, role, position[0:2]))
                self.updateFieldLimits()
        except AttributeError:
            pass

        canvas = FigureCanvas(fig)

        plt.grid(True)
        plt.xlim(self.fieldWidthLimits)
        plt.ylim(self.fieldHeightLimits)
        plt.close()

        self.polygonGraphicsScene.addWidget(canvas)

    def updateState(self):
        if self.externalTab.currentIndex() != 1:
            return

        data = self.session.get(f'{self.serverAddr}/server_control').json()
        updateStateTable(objectFromDict(data, ServerState), self.infoTable)

        data = self.session.get(f'{self.serverAddr}/data_player').json()
        updateStateTable(objectFromDict(data, PlayerItem), self.commandTable)

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
        self.setUnselected(self.robotTree.selectedItems())
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

        self.robotTree.addTopLevelItems([newRobot])

        newRobot.setText(0, 'New robot')
        newRobot.setSelected(True)

        self.robotCreatingWindow = RobotCreatingWindow(self)
        self.robotCreatingWindow.exec()

    def createNewTeam(self):
        self.setUnselected(self.teamTree.selectedItems())
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
        self.setUnselected(self.playerTree.selectedItems())

        if not self.teamTree.invisibleRootItem().childCount():
            return

        newPlayer = QTreeWidgetItem()
        defaultPlayer = PlayerParams()  # object for parsing default params

        for field in list(PlayerParams.__annotations__.keys())[1:]:
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultPlayer.__dict__.get(field)))
            newFieldItem.setToolTip(1, self.config.get('LOCALE', 'objectToolTip'))
            newPlayer.addChild(newFieldItem)

            if field in PLAYER_CUSTOM_FIELDS:
                self.playerTree.setItemWidget(newFieldItem, 1, createComboBoxSubwidget(self.width() // 5,
                                                                                       PlayerParams.aliases.get(field)))

        self.playerTree.addTopLevelItems([newPlayer])

        newPlayer.setText(0, 'New player')
        newPlayer.setSelected(True)

        playerList[self.currentTeamIndex].append(newPlayer)

        self.playerRolesWindow = PlayerRoleWindow(self)
        self.playerRolesWindow.exec_()

    def createNewObject(self):
        """
        Creates a new object and adds it into the tree.
        :return: None
        """
        self.setUnselected(self.objectTree.selectedItems())

        newObject = QTreeWidgetItem()
        defaultObject = ObjectParams()

        for field in list(ObjectParams.__annotations__.keys())[1:]:
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultObject.__dict__.get(field)))
            newFieldItem.setToolTip(1, self.config.get('LOCALE', 'objectToolTip'))
            newObject.addChild(newFieldItem)

        self.objectTree.addTopLevelItems([newObject])

        newObject.setText(0, "New object")
        newObject.setSelected(True)

        self.polygonRolesWindow = PolygonRoleWindow(self)
        self.polygonRolesWindow.exec()

    # Removing methods
    def removeRobot(self):
        root = self.robotTree.invisibleRootItem()
        for item in self.robotTree.selectedItems():
            if not item.childCount():
                continue
            (item.parent() or root).removeChild(item)
        self.isRobotSelected = False
        self.updateController()

    def removeAllRobots(self):
        reply = self.getReply(self.config.get('LOCALE', 'removeTitle'),
                              self.config.get('LOCALE', 'robotsRemoveText'))

        if reply == QMessageBox.No:
            return

        root = self.robotTree.invisibleRootItem()
        children = [root.child(i) for i in range(root.childCount())]
        for child in children:
            root.removeChild(child)
        self.updateController()

    def removeTeam(self):
        root = self.teamTree.invisibleRootItem()
        for item in self.teamTree.selectedItems():
            if not item.childCount():
                continue

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
        self.updateController()

    def removeAllTeams(self):
        reply = self.getReply(self.config.get('LOCALE', 'removeTitle'),
                              self.config.get('LOCALE', 'teamsRemoveText'))

        if reply == QMessageBox.No:
            return

        root = self.teamTree.invisibleRootItem()
        children = [root.child(i) for i in range(root.childCount())]
        for child in children:
            root.removeChild(child)

        teamList.clear()
        self.removeAllPlayersReinterpret()  # controller buttons will be updated automatically

    def removePlayer(self):
        root = self.playerTree.invisibleRootItem()
        for item in self.playerTree.selectedItems():
            if not item.childCount():
                continue
            (item.parent() or root).removeChild(item)
        self.isPlayerSelected = False
        self.updateController()

    def removeAllPlayers(self):
        reply = self.getReply(self.config.get('LOCALE', 'removeTitle'),
                              self.config.get('LOCALE', 'playersRemoveText'))

        if reply == QMessageBox.No:
            return

        root = self.playerTree.invisibleRootItem()
        selectedTeam = self.teamTree.selectedItems()[0]
        selectedTeamIdx = teamList.index(selectedTeam)
        children = playerList[selectedTeamIdx]

        # [1, 2, 3, 3, 4] -> [1, 2, 3, 4] if you try to remove 3 in straight order
        for i in range(len(children) - 1, -1, -1):
            root.removeChild(children[i])
            playerList[selectedTeamIdx].remove(children[i])

        self.updateController()

    def removeAllPlayersReinterpret(self):
        root = self.playerTree.invisibleRootItem()
        children = [root.child(i) for i in range(root.childCount())]
        for child in children:
            root.removeChild(child)
        playerList.clear()
        self.updateController()

    def removeObject(self):
        root = self.objectTree.invisibleRootItem()
        for item in self.objectTree.selectedItems():
            if not item.childCount():
                continue
            (item.parent() or root).removeChild(item)
        self.isObjectSelected = False

        self.updatePolygonPlots()
        self.updateController()

    def removeAllObjects(self):
        reply = self.getReply(self.config.get('LOCALE', 'removeTitle'),
                              self.config.get('LOCALE', 'objectsRemoveText'))

        if reply == QMessageBox.No:
            return

        root = self.objectTree.invisibleRootItem()
        children = [root.child(i) for i in range(root.childCount())]
        for child in children:
            root.removeChild(child)

        self.updatePolygonPlots()
        self.updateController()

    # Triggers
    def saveAs(self):
        """
        Saves JSON of the current tab.
        Dialog window with path selecting will be shown.
        :return: None
        """
        outputPath = getOutputPath(self, self.config.get("LOCALE", "getOutputPath"))
        if not outputPath:
            return

        if self.externalTab.currentIndex() == 0:
            self.exportPolygonJSON(outputPath)
        elif self.externalTab.currentIndex() == 1:
            self.exportRobotJSON(outputPath)
        else:
            self.exportTeamJSON(outputPath)

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

    def updateObjectLimits(self, objectCoords):
        self.minX = min([coord[0] for coord in objectCoords])
        self.maxX = max([coord[0] for coord in objectCoords])
        self.minY = min([coord[1] for coord in objectCoords])
        self.maxY = max([coord[1] for coord in objectCoords])

    def posChanged(self, item, column):
        """
        Updates polygon plots when position field has changed. The column must be equal 1.
        """
        if column:
            text = removeSpacesFromStr(item.text(1))
            if not re.compile('\\[-*\d+\.*\d*,-*\d+\.*\d*,-*\d+\.*\d*\\]').fullmatch(text) and \
                    not re.compile('\\(-*\d+\.*\d*,-*\d+\.*\d*,-*\d+\.*\d*\\)').fullmatch(text):
                self.showWarning(self.config.get('LOCALE', 'sizeError'))
                return

            self.removeOldCoords()
            newPosition = listFromStr(item.text(1))[0:2]
            self.objectsCoords.append(newPosition)
            self.updateObjectLimits(self.objectsCoords)
            self.updatePolygonPlots()

    def removeOldCoords(self):
        actualPositions = []
        root = self.objectTree.invisibleRootItem()
        children = [root.child(i) for i in range(root.childCount())]

        for child in children:
            position = listFromStr(child.child(getFieldIndex(child, 'position')).text(1))
            actualPositions.append(position[0:2])

        for pos in self.objectsCoords:
            if pos not in actualPositions:
                self.objectsCoords.remove(pos)

    def updateFieldLimits(self):
        """
        Updates field limits for the most correct drawing.
        Make sure that position coords is positive.
        :param newPos: list
        :return: None
        """
        newMinX = min([-abs(self.maxX * 0.25), abs(self.maxY * 0.25), self.minX * 1.25])
        newMaxX = max([abs(self.maxY * 0.25), abs(self.minY * 0.25), abs(self.minX * 0.25), self.maxX * 1.25])
        newMinY = min([-abs(self.maxY * 0.25), -abs(self.maxX * 0.25), self.minY * 1.25])
        newMaxY = max(abs(self.maxX * 0.25), abs(self.minX * 0.25), self.maxY * 1.25)
        self.fieldWidthLimits = [newMinX, newMaxX]
        self.fieldHeightLimits = [newMinY, newMaxY]

    def updateServerAddress(self):
        """
        Updates server address.
        :return: None
        """
        self.serverAddr = f"http://{self.hostname}:{self.port}/"

    # Actions
    def createPolygonParams(self):
        polygonParams = PolygonParams([])
        root = self.objectTree.invisibleRootItem()
        objectList = [root.child(i) for i in range(root.childCount())]

        for obj in objectList:
            dataclassPolygonObject = dataclassFromWidget(obj, ObjectParams(), self.objectTree)
            polygonParams.objects.append(dataclassPolygonObject)

        return polygonParams

    def exportPolygonJSON(self, outputPath):
        """
        Creates a JSON file using polygon dataclasses.
        The input data takes from the tree.
        :param outputPath: string
        :return: None
        """
        polygonParams = self.createPolygonParams()
        saveToFile(outputPath, json.dumps(dataclasses.asdict(polygonParams), indent=2))

    def createRobotParams(self):
        robotDataclasses = Robots([])
        root = self.robotTree.invisibleRootItem()
        objectList = [root.child(i) for i in range(root.childCount())]

        for obj in objectList:
            dataclassRobotFromWidget = dataclassFromWidget(obj, RobotParams(), self.robotTree)
            robotDataclasses.robotList.append(dataclassRobotFromWidget)

        return robotDataclasses

    def exportRobotJSON(self, outputPath):
        robotDataclass = self.createRobotParams()
        saveToFile(outputPath, json.dumps(dataclasses.asdict(robotDataclass), indent=2))

    def createTeamsParams(self):
        gameDataclass = Teams([])
        root = self.teamTree.invisibleRootItem()

        for i in range(root.childCount()):
            teamWidget = root.child(i)
            teamDataclass = dataclassFromWidget(teamWidget, TeamParams([]), self.teamTree)

            for player in playerList[i]:
                playerDataClass = dataclassFromWidget(player, PlayerParams(), self.playerTree)
                teamDataclass.players.append(playerDataClass)

            gameDataclass.teams.append(teamDataclass)

        return gameDataclass

    def exportTeamJSON(self, outputPath):
        gameDataclass = self.createTeamsParams()
        saveToFile(outputPath, json.dumps(dataclasses.asdict(gameDataclass), indent=2))

    def createGameParams(self):
        configDataclass = Config(teams=self.createTeamsParams().teams,
                                 polygon=self.createPolygonParams().objects,
                                 robots=self.createRobotParams().robotList)
        return configDataclass

    def exportGameJSON(self):
        outputPath = getOutputPath(self, self.config.get('LOCALE', 'getOutputPath'))
        if outputPath:
            configDataclass = self.createGameParams()
            saveToFile(outputPath, json.dumps(dataclasses.asdict(configDataclass), indent=2))

    def importJSON(self):
        filepath = getSelectedJson(self, 'Select file')
        try:
            extension = filepath.split('/')[-1].split('.')[-1]

            if extension == 'polygon':
                self.loadPolygonJSON(filepath)
            elif extension == 'robots':
                self.loadRobotJSON(filepath)
            elif extension == "players":
                self.importTeamJSON(filepath)
            elif extension == "game":
                self.importGameJSON(filepath)
            else:
                self.showWarning(self.config.get('LOCALE', 'wrongExtension'))
        except Exception:
            pass

    def loadPolygonJSON(self, filepath):
        """
        Loads Polygon's dataclass from the JSON file.
        """
        self.clearPolygonData()

        try:
            polygon = PolygonParams(**readJSON(filepath))
            polygon.objects = serializeChildren(polygon.objects, ObjectParams)
            fillObjectTree(polygon, self.objectTree, self.config)
            self.objectsCoords = [obj.position[0:2] for obj in polygon.objects]
            self.updateObjectLimits(self.objectsCoords)
            self.statusBar.showMessage(f"{self.config.get('LOCALE', 'jsonLabel')} {filepath.split('/')[-1]}", 10000)
            self.externalTab.setCurrentIndex(0)
        except TypeError:  # if file selecting was cancelled
            pass

        self.updatePolygonPlots()

    def loadRobotJSON(self, filepath):
        """
        Loads robot dataclass from the JSON file.
        """
        self.clearRobotData()

        try:
            robots = Robots(**readJSON(filepath))
            robots.robotList = serializeChildren(robots.robotList, RobotParams)
            fillRobotTree(robots, self.robotTree)
            self.statusBar.showMessage(f"{self.config.get('LOCALE', 'jsonLabel')} {filepath.split('/')[-1]}", 10000)
            self.externalTab.setCurrentIndex(1)
            self.isRobotsJsonSelected = True
        except TypeError:
            pass

    def importTeamJSON(self, filepath):
        """
        Loads team's dataclass from the JSON file.
        :param filepath: string
        :return: None
        """
        self.clearTeamData()

        try:
            teams = Teams(**readJSON(filepath))
            teams.teams = serializeChildren(teams.teams, TeamParams)

            for team in teams.teams:
                team.players = serializeChildren(team.players, PlayerParams)

            fillGameTree(teams, self.teamTree, self.playerTree)
            self.statusBar.showMessage(f"{self.config.get('LOCALE', 'jsonLabel')} {filepath.split('/')[-1]}", 10000)
            self.externalTab.setCurrentIndex(2)
            self.isTeamsJsonSelected = True
        except TypeError:
            pass

    def importGameJSON(self, filepath):
        """
        Imports selected by user .game (JSON) file.
        Widget trees will be updated automatically.
        Controller will be updated automatically.
        Polygon plots will be updated automatically.
        :return: None
        """
        self.clearPolygonData()
        self.clearRobotData()
        self.clearTeamData()

        try:
            cfg = Config(**readJSON(filepath))
            cfg.teams = serializeChildren(cfg.teams, TeamParams)
            cfg.robots = serializeChildren(cfg.robots, RobotParams)
            cfg.polygon = serializeChildren(cfg.polygon, ObjectParams)
        except TypeError:  # if file selecting was cancelled
            return

        for team in cfg.teams:
            team.players = serializeChildren(team.players, PlayerParams)

        fillObjectTree(PolygonParams(cfg.polygon), self.objectTree, self.config)
        fillRobotTree(Robots(cfg.robots), self.robotTree)
        fillGameTree(Teams(cfg.teams), self.teamTree, self.playerTree)

        self.objectsCoords = [obj.position[0:2] for obj in cfg.polygon]
        self.updateObjectLimits(self.objectsCoords)
        self.updatePolygonPlots()
        self.updateController()
        self.externalTab.setCurrentIndex(0)
        self.statusBar.showMessage(f'{self.config.get("LOCALE", "jsonLabel")} {filepath}', 10000)

    # Button controllers
    def isReadyToCreate(self):
        return self.objectTree.invisibleRootItem().childCount() and \
               self.robotTree.invisibleRootItem().childCount() and \
               self.teamTree.invisibleRootItem().childCount() and \
               self.playerTree.invisibleRootItem().childCount()

    def createGame(self):
        """
        Creates .game (JSON) file and sends it to the server over http.
        :return: None
        """
        if not self.isReadyToCreate():
            return

        configDataclass = self.createGameParams()

        try:
            self.session.post(f'{self.serverAddr}', params=dict(target='set',
                                                                type_command='core',
                                                                filename='game.game',
                                                                command='save_json'),
                              json=json.dumps(dataclasses.asdict(configDataclass), indent=2))
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

    def updateController(self):
        """
        Updates config buttons inside the GameController tab. Also updates status labels.
        :return: None
        """
        objectsCount = self.objectTree.invisibleRootItem().childCount()
        robotsCount = self.robotTree.invisibleRootItem().childCount()
        teamCount = self.teamTree.invisibleRootItem().childCount()
        playerCount = self.playerTree.invisibleRootItem().childCount()

        if not objectsCount:
            self.polygonCfgBttn.setEnabled(True)
            self.polygonLabel.setText(self.config.get('LOCALE', 'jsonLabelNot'))
        else:
            self.polygonCfgBttn.setEnabled(False)
            self.polygonLabel.setText(self.config.get('LOCALE', 'configWillBeCreated'))

        if not robotsCount:
            self.robotCfgBttn.setEnabled(True)
            self.robotsLabel.setText(self.config.get('LOCALE', 'jsonLabelNot'))
        else:
            self.robotCfgBttn.setEnabled(False)
            self.robotsLabel.setText(self.config.get('LOCALE', 'configWillBeCreated'))

        if (not playerCount) or (not teamCount):
            self.playerCfgBttn.setEnabled(True)
            self.teamsLabel.setText(self.config.get('LOCALE', 'jsonLabelNot'))
        else:
            self.playerCfgBttn.setEnabled(False)
            self.teamsLabel.setText(self.config.get('LOCALE', 'configWillBeCreated'))

        if (not objectsCount) or (not robotsCount) or (not teamCount) or (not playerCount):
            self.createGameBttn.setEnabled(False)
        else:
            self.createGameBttn.setEnabled(True)

    def changeSocketSettings(self):
        self.socketWindow = SocketSettingsWindow(self)
        self.socketWindow.show()

    # Clear methods
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

    def hideAllChildren(self, children):
        self.isPlayerSelected = False  # Don't allow removing players if player is hidden
        for child in children:
            child.setHidden(True)

    def setUnselected(self, selectedItems: list):
        for item in selectedItems:
            item.setSelected(False)

    # Localization
    def translateToRU(self):
        self.currentLocale = 'RU'
        self.objectRolesDict = createObjectRolesDict(self.currentLocale)
        self.playerRolesDict = createPlayerRolesDict(self.currentLocale)
        translateToRUS(self, 0)

    def translateToEN(self):
        self.currentLocale = 'EN'
        self.objectRolesDict = createObjectRolesDict(self.currentLocale)
        self.playerRolesDict = createPlayerRolesDict(self.currentLocale)
        translateToEN(self, 0)

    def getReply(self, title, text):
        return QMessageBox.question(self, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

    # Warnings
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
