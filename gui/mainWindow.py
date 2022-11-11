import dataclasses
import json

from utils.constants import *
from utils.guiMethods import *
from utils.templates import *

from classes.dataclasses import *

from gui.filterWindow import FilterWindow

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QTreeWidget, QPushButton, QTreeWidgetItem, QComboBox, QFontComboBox

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

        self.objectTree = self.findChild(QTreeWidget, 'objectTree')
        self.objectTree.itemDoubleClicked.connect(self.objectTreeDoubleClickTrigger)
        self.objectTree.itemClicked.connect(self.objectTreeItemClickTrigger)

        self.createJsonButton = self.findChild(QPushButton, 'createJsonButton')
        self.createJsonButton.clicked.connect(self.createJson)

        self.currentTeamIndex = 0

        # flags for item removing
        self.isTeamSelected = False
        self.isPlayerSelected = False
        self.isObjectSelected = False

    def addContextMenus(self):
        self.teamTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.teamTree.customContextMenuRequested.connect(self.showTeamTreeContextMenu)

        self.playerTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.playerTree.customContextMenuRequested.connect(self.showPlayerTreeContextMenu)

        self.objectTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.objectTree.customContextMenuRequested.connect(self.objectTreeContextMenu)

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
    def createNewTeam(self):
        newTeam = QTreeWidgetItem()
        defaultTeam = TeamParams([])

        for field in list(TeamParams.__annotations__.keys())[1:]:  # start from 1 cuz 0 is player list
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str((defaultTeam.__dict__.get(field))))
            newTeam.addChild(newFieldItem)

        newTeam.setText(0, 'New team')

        self.teamTree.addTopLevelItems([newTeam])
        teamList.append(newTeam)
        playerList.append([])

    def createNewPlayer(self):
        newPlayer = QTreeWidgetItem()
        defaultPlayer = PlayerParams()  # object for parsing default params

        for field in list(PlayerParams.__annotations__.keys()):
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

        for field in list(ObjectParams.__annotations__.keys()):
            newFieldItem = QTreeWidgetItem()
            newFieldItem.setText(0, field)
            newFieldItem.setText(1, str(defaultObject.__dict__.get(field)))
            newObject.addChild(newFieldItem)

            if field in OBJECT_CUSTOM_FIELDS:
                self.objectTree.setItemWidget(newFieldItem, 1, createComboBoxSubwidget(self.width() // 5,
                                                                                       ObjectParams.aliases.get(field)))

        newObject.setText(0, 'New object')

        self.objectTree.addTopLevelItems([newObject])

    # Removing methods
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

        try:
            self.teamTree.invisibleRootItem().child(0).setSelected(False)
        except AttributeError:  # if last item was removed
            pass

    def removePlayer(self):
        root = self.playerTree.invisibleRootItem()
        for item in self.playerTree.selectedItems():
            (item.parent() or root).removeChild(item)

    def removeObject(self):
        root = self.objectTree.invisibleRootItem()
        for item in self.objectTree.selectedItems():
            (item.parent() or root).removeChild(item)

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

    def objectTreeItemClickTrigger(self, item, col):
        self.isObjectSelected = True

        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def objectTreeDoubleClickTrigger(self, item, col):
        object_filter = item
        if item.text(0) == 'filter':
            self.filter = FilterWindow(self, object_filter)
            self.filter.show()

    def createJson(self):
        game = Game([])

        for i in range(self.teamTree.invisibleRootItem().childCount()):
            root = self.teamTree.invisibleRootItem()

            name_team = root.child(i).text(1)
            players = []

            try:
                color_team = list(map(int, self.teamTree.invisibleRootItem().child(i).child(0).text(1).split(',')))
            except ValueError:  # if color string is empty
                color_team = None  # will be set by dataclass as [0, 0, 0]

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

        objectList = []

        for i in range(self.objectTree.invisibleRootItem().childCount()):
            root = self.objectTree.invisibleRootItem()

            currObject = root.child(i)
            role = self.objectTree.itemWidget(currObject.child(0), 1).currentText()

            try:
                position = list(map(int, currObject.child(1).text(1).split(',')))
            except ValueError:
                position = None

            ind_for_led_controller = currObject.child(2).text(1)
            custom_settings = currObject.child(3).text(1)
            game_mechanics = currObject.child(4).text(1)
            filter = [list(map(int, arr)) for arr in [s.split(',') for s in currObject.child(5).text(1).split(';')]]

            objectParams = ObjectParams(role=role,
                                        position=position,
                                        ind_for_led_controller=ind_for_led_controller,
                                        custom_settings=custom_settings,
                                        game_mechanics=game_mechanics,
                                        filter=filter)
            objectList.append(objectParams)

        polygonParams = PolygonParams(objects=objectList)

        config = Config(game=game, polygon=polygonParams)

        with open('config.json', 'w') as output_file:
            output_file.write(json.dumps(dataclasses.asdict(config), indent=2))
            output_file.close()

    def hideAllChildren(self, children):
        self.isPlayerSelected = False  # Don't allow removing players if player is hidden
        for child in children:
            child.setHidden(True)

    @staticmethod
    def showAllChildren(children):
        for child in children:
            child.setHidden(False)
