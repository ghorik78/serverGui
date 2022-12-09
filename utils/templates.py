import configparser
import json
import random
import typing
import re
import matplotlib
import matplotlib.pyplot as plt

from PIL import Image

from database.database import *
from classes.dataclasses import *

from scipy import ndimage
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.image import imread

from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget, QComboBox, QFileDialog, QTableWidget, \
    QCheckBox, QTableWidgetItem, QHBoxLayout, QWidget, QPushButton


teamList = []
playerList = []  # first index -> team index from zero, second index -> player index from zero


def createStartPlaceFigures(fieldWidth: float, fieldHeight: float):
    startPlace = imread('images/startPlace.png')
    startPlaceRotated = ndimage.rotate(startPlace, 90)
    img = OffsetImage(startPlaceRotated, zoom=0.175)
    return [AnnotationBbox(img, (fieldWidth * 0.085, fieldHeight * 0.1), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.085, fieldHeight * 0.33), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.085, fieldHeight * 0.56), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.085, fieldHeight * 0.79), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.785, fieldHeight * 0.1), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.785, fieldHeight * 0.33), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.785, fieldHeight * 0.56), frameon=False),
            AnnotationBbox(img, (fieldWidth * 0.785, fieldHeight * 0.79), frameon=False)]


def createFigureByRole(currentLocale: str, role: str, pos: tuple):
    checkImage(getPathByAssert(currentLocale, role))
    imgFile = imread(getPathByAssert(currentLocale, role))
    img = OffsetImage(imgFile, zoom=0.15)

    return AnnotationBbox(img, pos, frameon=False)


def checkImage(path):
    img = Image.open(path)
    if img.size != (176, 176):
        img = img.resize((176, 176), Image.ANTIALIAS)
        img.save(path)
        img.close()


def resizeImage(image):
    image.resize((176, 176), Image.ANTIALIAS)


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


def dataclassFromWidget(widget: QTreeWidgetItem, outputClass, parentWidget: QTreeWidget):
    """
    Copies each field of widget to dataclass
    If datatype of dataclass field and widget field are different, function will change datatype of widget field
    :param widget: QTreeWidgetItem
    :param outputClass: Some dataclass
    :param parentWidget: QTreeWidget
    :return: Some dataclass
    """
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


def fillObjectTree(polygon: PolygonParams, tree: QTreeWidget, config: configparser.ConfigParser | None):
    """
    Fills the object tree using polygon dataclass.
    :param polygon: PolygonParams dataclass
    :param tree: QTreeWidget
    :param config: ConfigParser
    :return: None
    """
    for obj in polygon.objects:
        newObject = QTreeWidgetItem()
        for field in list(obj.__annotations__.keys())[1:]:
            fieldItem = QTreeWidgetItem()
            fieldItem.setText(0, str(field))
            fieldItem.setText(1, str(obj.__dict__.get(field)))
            fieldItem.setToolTip(1, "Press to change the field value.")
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


def fillComboBoxByRoles(rolesDict: dict, comboBox: QComboBox):
    comboBox.addItems(rolesDict.keys())


# Fills tree from game dataclass
def fillGameTree(game: Teams, teamTree: QTreeWidget, playerTree: QTreeWidget):
    """
    Fills the game tree by dataclass objects.
    After loading JSON file the program will set team 0 as current.
    The program will show items which is in team 0. Other objects will be hidden.
    :param game: Game dataclass
    :param teamTree: QTreeWidget
    :param playerTree: QTreeWidget
    :return: None
    """
    for team in game.teams:
        teamItem = QTreeWidgetItem()

        for field in list(team.__annotations__.keys())[2:]:
            fieldItem = QTreeWidgetItem()
            fieldItem.setText(0, str(field))
            fieldItem.setText(1, str(team.__dict__.get(field)))
            teamItem.addChild(fieldItem)

            teamList.append(teamItem)
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

            if game.teams.index(team) == 0:
                playerTree.addTopLevelItem(playerItem)


# Returns serialized from dictionary object
def objectFromDict(dictionary, outputClass):
    """
    Return serialized from dictionary object
    """
    return outputClass(**dictionary)


def updateStateTable(dataclass, table: QTableWidget):
    """
    Updates states table in GameController tab.
    :param dataclass: ServerState or PlayerItem dataclass
    :param table: QTableWidget
    :return: None
    """
    if dataclass.__class__ == ServerState:
        table.insertRow(0) if table.rowCount() == 0 else None
        items = [QTableWidgetItem(dataclass.version),
                 QTableWidgetItem(dataclass.state),
                 QTableWidgetItem(dataclass.gameTime)]
        for item in items:
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            table.setItem(0, items.index(item), item)

    if dataclass.__class__ == PlayerItem:
        currentRow = table.rowCount()
        table.insertRow(currentRow)

        checkBoxWidget = QWidget()
        blockCheckBox = QCheckBox()
        layout = QHBoxLayout(checkBoxWidget)
        layout.addWidget(blockCheckBox)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        table.setCellWidget(currentRow, 0, checkBoxWidget)

        buttonWidget = QWidget()
        blockButton = QPushButton('Block')
        layout = QHBoxLayout(buttonWidget)
        layout.addWidget(blockButton)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        table.setCellWidget(currentRow, 1, buttonWidget)

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


def serializeChildren(childrenList: list, childClass):
    """
    Returns list of serialized from JSON objects
    Will throw the TypeError if current dataclass and serialized are different (number of fields etc.)
    """
    return [childClass(**child) for child in childrenList]


def PlayerItemFromPlayerWidget(playerWidget: QTreeWidgetItem, playerId: int, command: str, ):
    """Return the dataclass object made from QTreeWidgetItem"""
    return PlayerItem(block=False,
                      off=False,
                      id=playerId,
                      command=command,
                      type='unknown',
                      state='unknown',
                      bullet=random.randint(10, 100),
                      balls=random.randint(10, 100),
                      cargo=False)


def readJSON(filepath: str) -> dict:
    """Returns dict from JSON file"""
    try:
        with open(filepath, 'r') as file:
            outputClass = json.loads(file.read())
            file.close()
        return outputClass
    except FileNotFoundError as e:  # if filepath is wrong
        pass


def getObjectPos(pos: list):
    return pos[0], pos[1]


def listFromStr(string: str):
    """Makes list (0, 0, 0) from string like '(0, 0, 0)'"""
    return [float(s) for s in re.findall(r'-?\d+\.?\d*', string)]


def removeDigitsFromStr(string: str):
    return ''.join([symbol for symbol in string if symbol.isalpha() or symbol.isspace()])


def removeSpacesFromStr(string: str):
    return ''.join([symbol for symbol in string if not symbol.isspace()])


def itemListToStr(items):
    """
    Returns array of string made from list of Widgets
    :param items: QTreeWidgetItem
    :return: list of str
    """
    return [item.text(0) for item in items]


def getMaxLengthOfField(fieldList: list):
    return max([len(field) for field in fieldList])


def getFieldIndex(widget: QTreeWidgetItem, fieldName: str):
    """Finds field index in the widget starting from zero"""
    for i in range(widget.childCount()):
        if widget.child(i).text(0) == fieldName:
            return i
    return None


def saveToFile(filename, data):
    """Saves data to the filename"""
    with open(filename, 'w') as file:
        file.write(data)
        file.close()


def getOutputPath(parent, title):
    return QFileDialog(parent, title).getSaveFileName()[0]


def getSelectedJson(parent, title: str):
    """Allows selecting only 1 JSON file"""
    return QFileDialog(parent, title).getOpenFileName()[0]


def getMultipleSelectedJson(parent):
    """Allows multiple selecting"""
    window = QFileDialog(parent, 'Select all JSON files')
    window.setFileMode(QFileDialog.ExistingFiles)
    return window.getOpenFileNames()[0]

