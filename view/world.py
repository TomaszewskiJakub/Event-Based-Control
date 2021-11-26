from PySide2 import QtWidgets, QtCore
import PySide2
from PySide2.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QTransform, qRgb
import numpy as np
from model.m_tree import tree_state
from time import time


class WorldDisplay(QtWidgets.QGraphicsView):
    def __init__(self, side=100):
        super(WorldDisplay, self).__init__()

        self.robot_pm = QPixmap("./images/Robot.png")
        if(self.robot_pm.isNull()):
            raise RuntimeError("Could not load Robot image")

        self.tree_pm = QPixmap("./images/Tree.png")
        if(self.tree_pm.isNull()):
            raise RuntimeError("Could not load Tree image")

        self.stump_pm = QPixmap("./images/Stump.png")
        if(self.stump_pm.isNull()):
            raise RuntimeError("Could not load Stump image")

        self.bridge_pm = QPixmap("./images/Bridge.png")
        if(self.bridge_pm.isNull()):
            raise RuntimeError("Could not load Bridge image")

        self.side = side
        self.setMinimumSize(500, 500)  # min-size of the widget
        self.setRenderHints(QPainter.Antialiasing)
        self._scene = QtWidgets.QGraphicsScene()
        self.setScene(self._scene)

        # self.generate_grid(15, 15, dropoff, parking)
        # self.draw_world(np.array(w))

    @QtCore.Slot()
    def update_world(self, robots, trees, stock_pile):
        s = time()
        for i in range(len(trees)):
            if(trees[i].state == tree_state.CUTTED):
                self._tree_items[i].setPixmap(self.stump_pm.scaled(
                            QtCore.QSize(self.side, self.side)
                        )
                    )

        for i in range(len(robots)):
            self._robot_items[i].setPos(
                robots[i].pose[1]*self.side,
                robots[i].pose[0]*self.side
            )

        if((stock_pile // 4 - 1) >= 0 and (stock_pile // 4 - 1) < len(self._bridge_items)):
            self._bridge_items[stock_pile // 4 - 1].show()
        print("Update time: ", time() - s)

    @QtCore.Slot()
    def init_world(self, robots, trees):
        s = time()
        self._tree_items = []
        self._robot_items = []
        self._bridge_items = []
        for tree in trees:
            if(tree.state == tree_state.GROWN):
                item = self._scene.addPixmap(
                        self.tree_pm.scaled(
                            QtCore.QSize(self.side, self.side)
                        )
                    )
                item.setPos(tree.pose[1]*self.side, tree.pose[0]*self.side)
                self._tree_items.append(item)

        for robot in robots:
            item = self._scene.addPixmap(
                    self.robot_pm.scaled(
                        QtCore.QSize(self.side, self.side)
                    )
                )
            item.setPos(robot.pose[1]*self.side, robot.pose[0]*self.side)
            self._robot_items.append(item)

        for i in range(1, 4):
            item = self._scene.addPixmap(
                    self.bridge_pm.scaled(
                        QtCore.QSize(self.side, self.side)
                    )
                )
            item.setPos((self._dropoff[1]+i)*self.side,
                        self._dropoff[0]*self.side)
            item.hide()
            self._bridge_items.append(item)

        print("Foreground: ", time()-s)
        # for i in range(w):
        #     for j in range(h):
        #         if(world[i][j] == "S"):
        #             item = self._scene.addPixmap(
        #                 self.stump_pm.scaled(
        #                     QtCore.QSize(self.side, self.side)
        #                 )
        #             )
        #             item.setPos(j*self.side, i*self.side)
        #         if(world[i][j] == "R"):
        #             item = self._scene.addPixmap(
        #                 self.robot_pm.scaled(
        #                     QtCore.QSize(self.side, self.side)
        #                 )
        #             )
        #             item.setPos(j*self.side, i*self.side)
        #         if(world[i][j] == "T"):
        #             item = self._scene.addPixmap(
        #                 self.tree_pm.scaled(
        #                     QtCore.QSize(self.side, self.side)
        #                 )
        #             )
        #             item.setPos(j*self.side, i*self.side)

    @QtCore.Slot()
    def generate_grid(self, columns, rows, dropoff, parking):
        s = time()
        self._scene.clear()
        print("Clearing: ", time()-s)
        rows += 8  # num of rows in grid

        grass = QBrush(QColor(qRgb(0, 154, 23)))  # background color of square
        road = QBrush(QColor(qRgb(25, 25, 25)))  # background color of square
        river = QBrush(QColor(qRgb(0, 0, 255)))  # background color of square
        drop = QBrush(QColor(qRgb(221, 160, 221)))  # background color of square
        pen = QPen(QtCore.Qt.black)  # border color of square

        rect = QtCore.QRectF(0, 0, self.side, self.side)
        for i in range(rows):
            for j in range(columns):
                if(i < rows-8 or i > rows-5):
                    self._scene.addRect(
                        rect.translated(
                            i * self.side,
                            j * self.side),
                        pen,
                        grass
                    )
                elif(i == rows-8):
                    self._scene.addRect(
                        rect.translated(
                            i * self.side,
                            j * self.side),
                        pen,
                        road
                    )
                else:
                    self._scene.addRect(
                        rect.translated(
                            i * self.side,
                            j * self.side),
                        pen,
                        river
                    )

        for square in parking:
            self._scene.addRect(
                rect.translated(
                    square[1] * self.side,
                    square[0] * self.side),
                pen,
                road
            )

        self._dropoff = dropoff
        self._scene.addRect(
            rect.translated(
                dropoff[1] * self.side,
                dropoff[0] * self.side),
            pen,
            drop
        )

        # this is required to ensure that fitInView works on first shown too
        self.resizeScene()
        print("Background: ", time()-s)

    def resizeScene(self):
        self.fitInView(self._scene.sceneRect())

    def resizeEvent(self, event):
        side = min(self.width(), self.height())
        self.resize(side, side)
        # call fitInView each time the widget is resized
        self.resizeScene()

    def showEvent(self, event):
        # call fitInView each time the widget is shown
        self.resizeScene()
