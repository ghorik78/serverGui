import random
import time

from utils.templates import *
from PyQt5.QtCore import QObject, QThread, QRunnable, pyqtSignal

import requests
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.image import imread, imsave
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Updater(QThread):
    s = pyqtSignal(float, float)
    def __init__(self):
        super().__init__()

    def run(self):
        self.s.emit(10, 0)
