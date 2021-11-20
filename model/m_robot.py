from enum import Enum
import threading
import random

class state(Enum):
    IDLE = 0
    MOVING = 1
    COLLECTING = 2
    DROPPING = 3
    READY = 4


class mRobot():
    def __init__(self, init_pose=[0, 0]):
        self.pose = init_pose
        self.state = state.IDLE

    def move_to(self, pose, i):
        self.state = state.MOVING
        timer = threading.Timer(random.uniform(0, 5), self._move_callback, pose)

    def _move_callback(self, pose):
        self.pose = pose
        self.state = state.READY
        # TODO: Emmit ready event

    def collect(self):
        self.state = state.COLLECTING
        timer = threading.Timer(random.uniform(0, 5), self._collect_callback)

    def _collect_callback(self):
        self.state = state.READY
        # TODO: Emmit ready event

    def drop(self):
        self.state = state.DROPPING
        timer = threading.Timer(random.uniform(0, 5), self._drop_callback)

    def _drop_callback(self):
        self.state = state.READY
        # TODO: Emmit ready event