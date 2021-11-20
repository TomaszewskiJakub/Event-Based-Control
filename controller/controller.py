from enum import Enum
from simulator import Simulator

class robot_State(Enum):
    IDLE = 0
    MOVING = 1
    COLLECTING = 2
    DROPPING = 3
    READY = 4

class tree_Stete(Enum):
    GROWN = 0
    PICKED = 1
    DELIVERED = 2
    ASSIGNED = 3

class Controller(QtCore.QObject):
    def __init__(self,  trees, robots):
        self.current_robots_position
        self.next_robots_position
        self.robots_state

        self.trees_position
        self.trees_state

        self.occupation_matrix
        self.missions

       


    def _init_occupation_matrix(self):
        """
        Wez listy robotów i drzew z symulatora: trees, robots 
        i zainicjalizuj macierz zajetości: 
        wolne miejsce - "0"
        robot - "r"
        drzewo - "t"
        """

    def _init_robots(self):
        """
        Wez liste robotów  z symulatora: robots 
        i zainicjalizuj  current_robots_position,
        next_robots_position oraz robots_state
        """

    def _init_trees(self):
        """
        Wez liste drzew  z symulatora: trees
        i zainicjalizuj trees_position oraz trees_state
        """

    def _init_missions(self):
        """
        zainicjalizuj puste listy 
        Misje będą wysznaczane w pętli programu:
        Zawsze kiedy program sprawdzi że jakiś robot ma pustą misje
        to wyznaczy mu nową,
        Tak więc w pierwszej iteracji programu zostaną wyznaczone 
        misje dla wszystkich robotów
        """
    
    def run(self)
        """

        """
    