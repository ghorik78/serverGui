from utils.constants import *
from utils.guiMethods import *
from utils.templates import *

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QWidget, QTreeWidget, QMenu, QAction, QTreeWidgetItem, QComboBox

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('uiFiles/gui.ui', self)

        self.addContextMenus()
        self.fillItemLists()

        self.teamTree = self.findChild(QTreeWidget, 'teamTree')  # list of teams
        self.teamTree.itemClicked.connect(self.showItemContextMenu)

        self.playerTree = self.findChild(QTreeWidget, 'playerTree')  # list of players
        self.playerTree.itemClicked.connect(self.showItemContextMenu)

        self.test = QTreeWidget()

    def addContextMenus(self):
        self.teamTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.teamTree.customContextMenuRequested.connect(self.showTeamTreeContextMenu)

        self.playerTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.playerTree.customContextMenuRequested.connect(self.showPlayerTreeContextMenu)

    def showTeamTreeContextMenu(self, position):
        menu, action = callTreeContextMenu('Create new team', self.teamTree, position)
        action.triggered.connect(self.createNewTeam)
        menu.exec_(self.teamTree.mapToGlobal(position))

    def showPlayerTreeContextMenu(self, position):
        menu, action = callTreeContextMenu('Create new player', self.playerTree, position)
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

    @staticmethod
    def showItemContextMenu(item, col):
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if (col == 0) and item.childCount() \
            else item.setFlags(DEFAULT_ITEM_FLAGS)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable) if col == 1 | item.childCount() \
            else None

    def fillItemLists(self):
        for i in range(self.teamTree.invisibleRootItem().childCount()):
            teamList.append(self.teamTree.invisibleRootItem().child(i))
        for i in range(self.playerTree.invisibleRootItem().childCount()):
            playerList.append(self.playerTree.invisibleRootItem().child(i))
