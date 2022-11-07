from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget


def callTreeContextMenu(createLabel, removeLabel, parent, isChildSelected):
    createAction = QAction(createLabel)
    removeAction = QAction(removeLabel) if isChildSelected else None
    menu = QMenu(parent)
    menu.addActions([createAction, removeAction])
    return menu, createAction, removeAction


def callObjectTeamSubmenu():
    pass


def itemListToStr(items):
    return [item.text(0) for item in items]
