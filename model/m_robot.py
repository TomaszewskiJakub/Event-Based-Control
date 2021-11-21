from enum import Enum
import threading
import random


class mRobot():
    def __init__(self, init_pose=[0, 0]):
        self.pose = init_pose


    def move_to(self, pose, i):
        timer = threading.Timer(random.uniform(0, 5), self._move_callback, pose)

    def _move_callback(self, pose):
        self.pose = pose
        # TODO: Emmit ready event

    def collect(self):
        timer = threading.Timer(random.uniform(0, 5), self._collect_callback)

    def _collect_callback(self):
        pass
        # TODO: Emmit ready event

    def drop(self):
        timer = threading.Timer(random.uniform(0, 5), self._drop_callback)

    def _drop_callback(self):
        pass
        # TODO: Emmit ready event