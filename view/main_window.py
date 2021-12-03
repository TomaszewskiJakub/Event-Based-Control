from PySide2 import QtWidgets, QtCore
from view.right_menu import RightMenu
from view.world import WorldDisplay
from view.consol_widget import Console
import numpy as np


class MainWindow(QtWidgets.QWidget):
    def __init__(self, simulator, controller):
        super(MainWindow, self).__init__()

        self._main_layout = QtWidgets.QHBoxLayout()
        self._right_layout = QtWidgets.QVBoxLayout()
        self._menu = RightMenu()
        self._display = WorldDisplay()
        self._simulator = simulator

        self._console = Console(simulator, controller)

        self.initUI()
        self.setWindowTitle("LumberBots")

        self._simulator.generateGrid.connect(self._display.generate_grid)
        self._simulator.initWorld.connect(self._display.init_world)
        self._simulator.updateWorld.connect(self._display.update_world)
        self._menu.sendData.connect(self._simulator.generate)
        self._simulator.logMessage.connect(self._console.add_log)
        self._menu.logMessage.connect(self._console.add_log)

    def initUI(self):
        # self._menu.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self._right_layout.addWidget(self._menu)
        # self._console.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self._right_layout.addWidget(self._console)

        self._main_layout.addWidget(self._display)
        self._main_layout.addLayout(self._right_layout)

        self.setLayout(self._main_layout)
