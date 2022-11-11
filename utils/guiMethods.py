from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget, QComboBox


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
    return comboBox


def itemListToStr(items):  # used for adding filters
    return [item.text(0) for item in items]


def getMaxLengthOfField(fieldList: list):
    return max([len(field) for field in fieldList])
