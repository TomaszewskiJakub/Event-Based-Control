from PySide2 import QtWidgets, QtCore
from view.right_menu import RightMenu
from view.world import WorldDisplay
import numpy as np

class MainWindow(QtWidgets.QWidget):
    def __init__(self, simulator):
        super(MainWindow, self).__init__()

        self._main_layout = QtWidgets.QHBoxLayout()
        self._menu = RightMenu()
        self._display = WorldDisplay()
        self._simulator = simulator

        self.initUI()
        self.setWindowTitle("LumberBots")

        self._simulator.generateGrid.connect(self._display.generate_grid)
        self._simulator.drawWorld.connect(self._display.draw_world)
        self._menu.sendData.connect(self._simulator.generate)

    def initUI(self):
        self._menu.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self._main_layout.addWidget(self._display, 1)
        self._main_layout.addWidget(self._menu)

        self.setLayout(self._main_layout)
