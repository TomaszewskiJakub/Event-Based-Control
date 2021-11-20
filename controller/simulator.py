from typing import Tuple
from PySide2 import QtCore
from queue import Queue
import random
from model.m_tree import mTree
from model.m_robot import mRobot


class SimulatorThread(QtCore.QThread):
    def __init__(self, app):
        super(SimulatorThread, self).__init__(parent=None)
        self._app = app

    def run(self):
        print("Starting simulator")
        self._app.run()


class Simulator(QtCore.QObject):
    generateGrid = QtCore.Signal(int, int, list, list)
    drawWorld = QtCore.Signal(list, list)
    worldGenerated = QtCore.Signal(list, list, int, int)

    def __init__(self):
        super(Simulator, self).__init__()
        self._controlable_que = Queue()
        self._observable_que = None
        self._trees = []
        self._robots = []
        self._stock_pile = 0

    @property
    def trees(self):
        return self._trees

    @property
    def robots(self):
        return self._robots

    @property
    def stock_pile(self):
        return self._stock_pile

    @property
    def controllable_que(self):
        return self._controlable_que

    @property
    def observable_que(self):
        return self._observable_que

    @observable_que.setter
    def observable_que(self, var):
        self._observable_que = var

    @QtCore.Slot()
    def generate(self, width, height, num_robots, num_trees, x_margin=3, y_margin=4):
        print("Calling generate")
        self._width = width
        self._height = height

        self.dropoff = [height//2, width]

        for i in range(num_trees):
            y = random.randrange(0, width - x_margin)
            x = random.randrange(y_margin, height)

            self._trees.append(mTree([x, y]))

        parking = []
        for i in range(num_robots):
            self._robots.append(mRobot([0, i]))
            parking.append([0, i])

        self.generateGrid.emit(width, height, self.dropoff, parking)
        self.drawWorld.emit(self._robots, self._trees)
        self.worldGenerated.emit(
            self._robots,
            self._trees,
            self._height,
            self._width
        )



    # def run(self):
    #     while(True):
    #         while not self._controlable_que.empty():
    #             # Process all incoming contollable events
    #             # Take element from queue and delete it                    
    #             event = self._controlable_que.get_nowait()

    #             event = event.split("_")
