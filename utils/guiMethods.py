from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget


def callTreeContextMenu(label, parent):
    action = QAction(label)
    menu = QMenu(parent)
    menu.addAction(action)
    return menu, action

