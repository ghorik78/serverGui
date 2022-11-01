from PyQt5 import Qt, QtCore
from PyQt5.QtWidgets import QMenu, QAction


def callTreeContextMenu(label: str, parent, pos):
    action = QAction(label)
    menu = QMenu(parent)
    menu.addAction(action)
    return menu, action