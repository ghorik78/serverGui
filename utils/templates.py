import json

from classes.dataclasses import *

from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget, QComboBox, QFileDialog, QTableWidget, \
    QCheckBox, QTableWidgetItem, QHBoxLayout, QWidget

import typing
import re

teamList = []
playerList = []  # first index -> team index from zero, second index -> player index from zero


def callTreeContextMenu(createLabel, removeLabel, parent, isChildSelected):  # tree context menus for main window
    createAction = QAction(createLabel)
    removeAction = QAction(removeLabel) if isChildSelected else None
    menu = QMenu(parent)
    menu.addActions([createAction, removeAction])
    return menu, createAction, removeAction


def createComboBoxSubwidget(width: int, items: list):
    comboBox = QComboBox()
    comboBox.setMaximumWidth(width)
    comboBox.addItems(items)
    comboBox.setStyleSheet("border: 1px solid grey;")
    return comboBox


# Copies each field of widget to dataclass
# If datatype of dataclass field and widget field are different, function will change datatype of widget field
def dataclassFromWidget(widget: QTreeWidgetItem, outputClass, parentWidget: QTreeWidget):
    obj = outputClass

    obj.__dict__['title'] = widget.text(0)

    for field in [widget.child(i) for i in range(widget.childCount())]:
        # Saves text of combo box widget
        if field.text(0) in OBJECT_CUSTOM_FIELDS + ROBOT_CUSTOM_FIELDS + PLAYER_CUSTOM_FIELDS:
            obj.__dict__[field.text(0)] = parentWidget.itemWidget(widget.child(getFieldIndex(widget, field.text(0))),
                                                                  1).currentText()

        elif obj.__dict__.get(field.text(0)).__class__ == tuple:
            obj.__dict__[field.text(0)] = listFromStr(field.text(1))

        elif obj.__dict__.get(field.text(0)).__class__ == int:
            obj.__dict__[field.text(0)] = int(field.text(1))

        elif obj.__dict__.get(field.text(0)).__class__ == float:
            obj.__dict__[field.text(0)] = float(field.text(1))

        else:
            obj.__dict__[field.text(0)] = field.text(1)

    return obj


def fillObjectTree(polygon: PolygonParams, tree: QTreeWidget):
    for obj in polygon.objects:
        newObject = QTreeWidgetItem()
        for field in list(obj.__annotations__.keys())[1:]:
            fieldItem = QTreeWidgetItem()
            fieldItem.setText(0, str(field))
            fieldItem.setText(1, str(obj.__dict__.get(field)))
            newObject.addChild(fieldItem)

        newObject.setText(0, obj.__dict__.get('title'))
        tree.addTopLevelItem(newObject)


def fillRobotTree(robots: Robots, tree: QTreeWidget):
    for robot in robots.robotList:
        newRobot = QTreeWidgetItem()
        for field in list(robot.__annotations__.keys())[1:]:
            fieldItem = QTreeWidgetItem()
            fieldItem.setText(0, str(field))
            fieldItem.setText(1, str(robot.__dict__.get(field)))
            newRobot.addChild(fieldItem)

            # Creating comboBox for special field
            # Special == needs comboBox
            if field in ROBOT_CUSTOM_FIELDS:
                tempComboBox = createComboBoxSubwidget(tree.parentWidget().width() // 5,
                                                       RobotParams.aliases.get(field))
                tempComboBox.setCurrentText(robot.__dict__.get(field))
                tree.setItemWidget(fieldItem, 1, tempComboBox)

        newRobot.setText(0, robot.__dict__.get('title'))
        tree.addTopLevelItem(newRobot)


# Fills tree from game dataclass
def fillGameTree(game: Game, teamTree: QTreeWidget, playerTree: QTreeWidget):
    for team in game.teams:
        teamItem = QTreeWidgetItem()

        for field in list(team.__annotations__.keys())[2:]:
            fieldItem = QTreeWidgetItem()
            fieldItem.setText(0, str(field))
            fieldItem.setText(1, str(team.__dict__.get(field)))
            teamItem.addChild(fieldItem)

            teamList.append([teamItem])
            playerList.append([])

        teamItem.setText(0, team.__dict__.get('title'))
        teamTree.addTopLevelItem(teamItem)

        for player in team.players:
            playerItem = QTreeWidgetItem()

            for field in list(player.__annotations__.keys())[1:]:
                fieldItem = QTreeWidgetItem()
                fieldItem.setText(0, str(field))
                fieldItem.setText(1, str(player.__dict__.get(field)))
                playerItem.addChild(fieldItem)

                if field in PLAYER_CUSTOM_FIELDS:
                    playerTree.setItemWidget(fieldItem, 1,
                                             createComboBoxSubwidget(playerTree.parentWidget().width() // 5,
                                                                     PlayerParams.aliases.get(
                                                                         field)))

            playerList[game.teams.index(team)].append(playerItem)

            playerItem.setText(0, player.__dict__.get('title'))

            # After loading JSON file the program will set team 0 as current
            # The program will show items which is in team 0
            # Other objects will be hidden
            if game.teams.index(team) == 0:
                playerTree.addTopLevelItem(playerItem)


# Returns serialized from dictionary object
def objectFromDict(dictionary, outputClass):
    return outputClass(**dictionary)


def updateStateTable(dataclass, table: QTableWidget):
    if dataclass.__class__ == ServerState:
        table.insertRow(0)
        items = [QTableWidgetItem(dataclass.version),
                 QTableWidgetItem(dataclass.state),
                 QTableWidgetItem(dataclass.gameTime)]
        for item in items:
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(0, items.index(item), item)

    if dataclass.__class__ == Command:
        currentRow = table.rowCount()
        table.insertRow(currentRow)

        widget = QWidget()
        cb = QCheckBox()
        layout = QHBoxLayout(widget)
        layout.addWidget(cb)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        table.setCellWidget(currentRow, 0, widget)

        items = [QTableWidgetItem(str(dataclass.id)),
                 QTableWidgetItem(dataclass.command),
                 QTableWidgetItem(dataclass.type),
                 QTableWidgetItem(dataclass.state),
                 QTableWidgetItem(str(dataclass.bullet)),
                 QTableWidgetItem(str(dataclass.balls)),
                 QTableWidgetItem(str(dataclass.cargo))]
        for item in items:
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(currentRow, items.index(item) + 2, item)

        # block: bool = False
        # off: bool = False
        # id: int = 0
        # command: str = 'unknown'
        # type: str = 'unknown'
        # state: str = 'unknown'
        # bullet: int = 0
        # balls: int = 0
        # cargo: bool = False


# Returns list of serialized from JSON objects
# Will throw the TypeError if current dataclass and serialized are different (number of fields etc.)
def serializeChildren(childrenList: list, childClass):
    return [childClass(**child) for child in childrenList]


# Return dict from JSON file
def readJSON(filepath: str):
    try:
        with open(filepath, 'r') as file:
            outputClass = json.loads(file.read())
            file.close()
        return outputClass
    except FileNotFoundError as e:  # if filepath is wrong
        pass


# Makes list (0, 0, 0) from string like '(0, 0, 0)'
def listFromStr(string: str):
    return [float(s) for s in re.findall(r'-?\d+\.?\d*', string)]


def itemListToStr(items):  # used for adding filters
    return [item.text(0) for item in items]


def getMaxLengthOfField(fieldList: list):
    return max([len(field) for field in fieldList])


def getFieldIndex(widget: QTreeWidgetItem, fieldName: str):
    for i in range(widget.childCount()):
        if widget.child(i).text(0) == fieldName:
            return i
    return None


def saveToFile(filename, data):
    with open(filename, 'w') as file:
        file.write(data)
        file.close()


def getSelectedJson(parent, title: str):
    return QFileDialog(parent, title).getOpenFileName()[0]
