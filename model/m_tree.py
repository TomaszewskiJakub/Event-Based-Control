from enum import Enum


class tree_state(Enum):
    GROWN = 0
    CUTTED = 1


class mTree():
    def __init__(self, init_pose=[0, 0]):
        self.pose = init_pose
        self.state = tree_state.GROWN

    def cut(self):
        self.state = tree_state.CUTTED