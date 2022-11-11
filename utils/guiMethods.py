from classes.dataclasses import *

from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget, QComboBox

import typing
import re


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


# Copies each field of widget to dataclass
# If datatype of dataclass field and widget field are different, function will change datatype of widget field
def dataclassFromWidget(widget: QTreeWidgetItem, outputClass):
    obj = outputClass

    for field in [widget.child(i) for i in range(widget.childCount())]:
        if obj.__dict__.get(field.text(0)).__class__ == tuple:
            obj.__dict__[field.text(0)] = listFromStr(field.text(1))

        elif obj.__dict__.get(field.text(0)).__class__ == int:
            obj.__dict__[field.text(0)] = int(field.text(1))

        elif obj.__dict__.get(field.text(0)).__class__ == float:
            obj.__dict__[field.text(0)] = float(field.text(1))

        else:
            obj.__dict__[field.text(0)] = field.text(1)

    return obj


# Makes list (0, 0, 0) from string like '(0, 0, 0)'
def listFromStr(string: str):
    return [float(s) for s in re.findall(r'-?\d+\.?\d*', string)]


def itemListToStr(items):  # used for adding filters
    return [item.text(0) for item in items]


def getMaxLengthOfField(fieldList: list):
    return max([len(field) for field in fieldList])
