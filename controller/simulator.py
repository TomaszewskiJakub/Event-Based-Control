from time import sleep
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
    initWorld = QtCore.Signal(list, list)
    updateWorld = QtCore.Signal(list, list, int)
    worldGenerated = QtCore.Signal(list, list, int, int)
    logMessage = QtCore.Signal(str)

    def __init__(self):
        super(Simulator, self).__init__()
        self._controllable_que = Queue()
        self._observable_que = None
        self._trees = []
        self._robots = []
        self._stock_pile = 0
        self._prev_stock_pile = 0
        self._is_generated = False

    @property
    def is_generated(self):
        return self._is_generated

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
        return self._controllable_que

    @property
    def observable_que(self):
        return self._observable_que

    @observable_que.setter
    def observable_que(self, var):
        self._observable_que = var

    @QtCore.Slot()
    def generate(self, width, height, num_robots, num_trees, sim_speed, x_margin=3, y_margin=4):
        self.logMessage.emit("Generating World...")
        self._width = width
        self._height = height

        self.dropoff = [width, height // 2]

        self.logMessage.emit("Spawning trees...")
        for i in range(num_trees):
            generated = False
            while not generated:
                x = random.randrange(0, width - x_margin)
                y = random.randrange(y_margin, height)

                # Check to pose of all trees so we don't spawn trees one on another
                # If the ANY pose repeats the any(*) returns true, so it needs
                # to be negated so generated is false.
                generated = not any([[x, y] == tree.pose for tree in self._trees])

            self._trees.append(mTree([x, y]))

        for tree in self._trees:
            print(tree.pose)

        self.logMessage.emit("Spawning robots...")
        self._parking = []
        for i in range(num_robots):
            self._robots.append(mRobot(i, self._observable_que, sim_speed, [i, 0]))
            self._parking.append([i, 0])

        self.generateGrid.emit(height, width, self.dropoff, self._parking)
        self.initWorld.emit(self._robots, self._trees)

        self.worldGenerated.emit(self._robots, self._trees, self._height, self._width)
        self.logMessage.emit("World created successfully!")
        self._is_generated = True

    def run(self):
        last_update = 0
        while True:
            # print("Executing Simulator while")
            while not self._controllable_que.empty():
                # Process all incoming contollable events
                # Take element from queue and delete it
                event = self._controllable_que.get_nowait()
                event = event.split("_")

                # print(event)

                if event[0] == "move":
                    # We need to cast the indexes to int because after split they
                    # are still strings
                    self._robots[int(event[1])].move_to([int(event[2]), int(event[3])])

                if event[0] == "pick":
                    # We need to cast the indexes to int because after split they
                    # are still strings
                    self._robots[int(event[1])].collect(self._trees[int(event[2])])

                if event[0] == "drop":
                    # We need to cast the indexes to int because after split they
                    # are still strings
                    self._robots[int(event[1])].drop()
                    # Increment the number of wood in the stockpile
                    self._stock_pile += 1
            
            sleep(0.001)

            # Update the Graphics if something has changed
            # if self.check_update():
            #     s = time.time()
            #     print("Sending update")
            #     self.updateWorld.emit(self.robots, self._trees, self._stock_pile)
            #     # print("Rate: ", 1/(s-last_update))
            #     last_update=s
                

    def check_update(self):
        update = False
        for robot in self._robots:
            if robot.updated:
                robot.updated = False
                update = True

        for tree in self._trees:
            if tree.updated:
                tree.updated = False
                update = True

        if self._stock_pile != self._prev_stock_pile:
            self._prev_stock_pile = self._stock_pile
            update = True

        return update
