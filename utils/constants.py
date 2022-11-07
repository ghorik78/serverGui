from PyQt5 import QtWidgets, Qt, QtCore

DEFAULT_ITEM_FLAGS = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled

CONTROL_OBJECTS = ['EduBotObject', 'PioneerObject']
ROLES = ['RoboFinist_Role']
OBJECT_ROLES = ['Fabric_RolePolygon', 'TakeoffArea_RolePolygon', 'Weapoint_RolePolygon']
TEAM_LIST_STR = []