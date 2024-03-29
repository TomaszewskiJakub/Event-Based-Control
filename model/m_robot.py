import threading
import random
from time import time

class mRobot():
    def __init__(self, id, obsv_que, sim_speed, init_pose=[0, 0]):
        self.pose = init_pose
        self.updated = False
        self._obsv_que = obsv_que
        self._id = id
        self._sim_speed = sim_speed
        print("Sim speed: ", self._sim_speed)

    def move_to(self, pose):
        timer = threading.Timer(self._sim_speed, self._move_callback, [pose])
        timer.start()

    def _move_callback(self, pose):
        self.pose = pose
        # Send ready event to controller
        self._obsv_que.put("ready_{}".format(self._id))
        self.updated = True

    def collect(self, tree):
        timer = threading.Timer(self._sim_speed, self._collect_callback, [tree])
        timer.start()

    def _collect_callback(self, tree):
        # Send ready and change the state of the tree
        self._obsv_que.put("ready_{}".format(self._id))
        tree.cut()

    def drop(self):
        timer = threading.Timer(self._sim_speed, self._drop_callback)
        timer.start()

    def _drop_callback(self):
        # Send ready and increment the number od wood in the stockpile
        self._obsv_que.put("ready_{}".format(self._id))
