import sys

from PyQt5 import QtWidgets, QtGui
from gui.mainWindow import MainWindow

app = QtWidgets.QApplication(sys.argv)

a = [0]
a.remove(0)

window = MainWindow()
window.show()

app.exec_()