from enum import Enum
from queue import Queue
from PySide2 import QtCore
import numpy as np
from numpy.core.records import array
from gridGraph import GridGraph


class robot_State(Enum):
    IDLE = 0
    MOVING = 1
    COLLECTING = 2
    DROPPING = 3
    READY = 4


class tree_Stete(Enum):
    GROWN = 0
    PICKED = 1
    ASSIGNED = 2


# Struktura eventu:
# 1. Każdy event zapamiętywany jest jako string
# 2. Struktura stringu
#    move_robot_id_x'_y'
#    pick_robot_id_treeID
#    drop_robot_id
#    ready_robot_id
# 3. Example:
# tmp =  "move_1_2_3"
# tmp.split("_") = splitted  # ["move", "1", "2", "3"]
# action = splitted[0]
# id = splitted[1]
# xp = splitted[2]
# yp = splitted[3]


class Controller(QtCore.QObject):
    def __init__(self):
        self._current_robots_position = []
        self._next_robots_position = []
        self._robots_state = []

        self._trees_position = []
        self._trees_state = []

        self._occupation_matrix = None
        self._missions = []

        self._observable_que = Queue()
        self._controllable_que = None

        self._width = -1
        self._height = -1

        self._drop_position = []
        self._stock_pile = 0

        self.graph = None

    @property
    def observable_que(self):
        return self._observable_que

    @property
    def controllable_que(self):
        return self._controllable_que

    @controllable_que.setter
    def controllable_que(self, var):
        self._controllable_que = var

    @QtCore.Slot()
    def init_all(self, robots, trees, height, width):
        """
        Sygnał inicializujący Controller
        """
        print("initing controller")
        self.graph = GridGraph(width, height)
        self._drop_position = [width, height//2]
        self._init_robots(robots)
        self._init_trees(trees)
        self._init_occupation_matrix(trees, robots, height, width)
        self._init_missions()
        self._generate_mission(1)

    def _init_occupation_matrix(self, trees, robots, height, width):
        """
        Wez listy robotów i drzew z symulatora: trees, robots
        i zainicjalizuj macierz zajetości:
        wolne miejsce - "0"
        robot - "r"
        drzewo - "t"
        """

        tmp_arr = [['0' for i in range(width)] for j in range(height)]
        tmp_arr = np.array(tmp_arr)
        self._occupation_matrix = tmp_arr
        for robot in robots:
            self._occupation_matrix[robot.pose[0], robot.pose[1]] = 'r'

        for tree in trees:
            self._occupation_matrix[tree.pose[0], tree.pose[1]] = 't'

        # Just for debugging
        # print("Initialized _occupation_matrix: ",self._occupation_matrix)

    def _init_robots(self, robots):
        """
        Wez liste robotów  z symulatora: robots
        i zainicjalizuj  current_robots_position,
        next_robots_position oraz robots_state
        """
        for robot in robots:
            self._current_robots_position.append(robot.pose)
            self._next_robots_position.append(None)
            self._robots_state.append(robot_State.IDLE)

        # Just for debugging
        print("Initialized _current_robots_position:",
              self._current_robots_position)
        print("Initialized _next_robots_position:",
              self._next_robots_position)
        print("Initialized _robots_state:",
              self._robots_state)

    def _init_trees(self, trees):
        """
        Wez liste drzew  z symulatora: trees
        i zainicjalizuj trees_position oraz trees_state
        """
        for tree in trees:
            self._trees_position.append(tree.pose)
            self._trees_state.append(tree_Stete.GROWN)

        # Just for debugging
        print("Initialized _trees_position:", self._trees_position)
        print("Initialized _trees_state:", self._trees_state)

    def _init_missions(self):
        """
        zainicjalizuj puste listy
        Misje będą wysznaczane w pętli programu:
        Zawsze kiedy program sprawdzi że jakiś robot ma pustą misje
        to wyznaczy mu nową,
        Tak więc w pierwszej iteracji programu zostaną wyznaczone
        misje dla wszystkich robotów
        """
        self._missions = [None for i in range(len(self._robots_state))]

        # Just for debugging
        print("Initialized _missions:", self._missions)

    def run(self):
        """
        Głowna pętla programu.
        """
        while(True):
            acceptable_events = []
            # 1. Przetworz kolejke obserwowalnych i zaktualizuj stan (wywolaj
            #    główną funkcje, w niej iterujemy dopóki kolejka obserwowalnych
            #    nie jest pusta)
            # 2. Przejdz po misjach wszystkich robotów
            #   2.1 Jesli pusta wygeneruj
            #   2.2 Jesli nie pusta, weź pierwsze zdanie, sprawdz za pomoca
            #       funcji gamma (dla odpowiedniego eventu) czy jest mozliwa
            #       do wykonania, jeżeli możliwa dodaj do listy mozliwych do
            #       wykonania.
            # 3. Weź optymalny event z acceptable_events
            # 4. Zaktualizuj wewnętrzny stan na podstawie wybranego zadania
            # 5. Dodaj wybrane zadanie do kolejki controllable_que

            pass

    def _gamma(self, event):
        """
        W zależności od eventu wywołaj odpowiednia gamme
        """
        l_event = event.split("_")
        if l_event[0] == "move":
            return self._gamma_move(l_event)

        if l_event[0] == "pick":
            return self._gamma_pick(l_event)

        if l_event[0] == "drop":
            return self._gamma_drop(l_event)

    def _gamma_move(self, l_event):
        """
        Sprawdza czy event move jest możliwy do wykonania
        """
        robot_id = l_event[1]
        x_prim = l_event[2]
        y_prim = l_event[3]

        # jeśli robot może przejeżdzać po drzewach to trzeba dodać '0' or 't'
        if (self._occupation_matrix[x_prim, y_prim] == '0' or
            self._occupation_matrix[x_prim, y_prim] == 't') and \
           (self._robots_state[robot_id] == robot_State.READY or
           self._robots_state[robot_id] == robot_State.IDLE):
            return True
        return False

    def _gamma_pick(self, l_event):
        """
        Sprawdza czy event pick jest możliwy do wykonania
        """
        robot_id = l_event[1]
        treeID = l_event[1]

        if self._current_robots_position[robot_id] ==\
           self._trees_position[treeID] and \
           self._robots_state[robot_id] == robot_State.READY:
            return True
        return False

    def _gamma_drop(self, l_event):
        """
        Sprawdza czy event drop jest możliwy do wykonania
        """
        robot_id = l_event[1]

        if self._current_robots_position[robot_id] == self._drop_position and \
           self._robots_state[robot_id] == robot_State.READY:
            return True
        return False

    def _generate_mission(self, robot_id):
        """
        Generuje całą misje dla danego robota.
        1. Od robota do drzewa i zetnij
        2. Od drzewa do wjadzu
        3. Od wjazdu do magazynu, upusc, od magazynu do wyjazdu
        4. Od wyjzdu do parkingu
        """
        desired_tree_position = self._trees_position[robot_id]
        robot_position = self._current_robots_position[robot_id]
        start = tuple(robot_position)
        goal = tuple(desired_tree_position)
        print("start", start)
        print("goal", goal)

        came_from, cost_so_far = self.graph.a_star_search(self.graph,
                                                          start, goal)
        self.graph.draw_grid(self.graph,
                             point_to=came_from,
                             start=start, goal=goal)
        self.graph.draw_grid(self.graph,
                             path=self.graph.reconstruct_path(came_from,
                                                              start=start,
                                                              goal=goal))
        print(self.graph.reconstruct_path(came_from, start=start, goal=goal))

    def _mission_collect_tree(self, robot_id):
        """
        Generuje ścieżkę od akutalniej pozycji robota do drzewa i dodaje do
        niej event pick.
        1. Wybieramy najbliższe drzewo, które ma stan GROWN

        zwraca ścieżkę i id'k wybranego drzewa
        """
        pass

    def _mission_2_entrance(self, robot_id, tree_id):
        """
        Generuje ścieżkę od wybranwgo drzewa do wjazdu (żeby stanął na
        pierwszym kafelku drogi).
        """
        pass

    def _mission_road(self, robot_id):
        """
        Generuj ruch po drodze do magazynu, odstawienie drzewa, i ruch od
        magazynu do wyjazdu (żeby stanął na ostatnim kafelku drogi).
        """
        pass

    def _mission_2_parking(self, robot_id):
        """
        Generuj ruch od aktualniej pozycji robota do jego miejsca w parkingu
        """
        pass

    def _update_state_ready(self):
        """
        Przetwarzaj tak długo jak kolejka obserwowalnych nie jest pusta.
        Aktualizuj stan na podstawie aktualnego stanu.
        """
        while not self._observable_que.empty():
            event = self._observable_que.get_nowait()
            l_event = event.split("_")
            robot_id = l_event[1]
            if self._robots_state[robot_id] == robot_State.COLLECTING:
                self._update_ready_collecting(robot_id)

            if self._robots_state[robot_id] == robot_State.DROPPING:
                self._update_ready_dropping(robot_id)

            if self._robots_state[robot_id] == robot_State.MOVING and\
               not self._missions[robot_id].empty():
                self._update_ready_moving_notEmpty(robot_id)

            if self._robots_state[robot_id] == robot_State.MOVING and\
               self._missions[robot_id].empty():
                self._update_ready_moving_empty(robot_id)

    def _update_ready_collecting(self, robot_id):
        """
        Ready i aktualny stan collecting
        """
        # stan robota zmienia się na ready
        self._robots_state[robot_id] = robot_State.READY
        # stan drzewa zmienia się a picked -> potrzebne id drzewa
        # potrzebne jest id_drzewa do zmiany stanu.
        tree_id = self._trees_position.index(
                  self._current_robots_position[robot_id])
        self._trees_state[tree_id] = tree_Stete.PICKED

        # usunąć drzewo z macierzy zajętości? nie, ponieważ:
        # załatwia to już zmiana na 'r' w momencie gdy robot stanie na polu
        # a gdy z niego wyjedzie zostanie tam ustawiona warość '0'

    def _update_ready_dropping(self, robot_id):
        """
        Ready i aktualny stan dropping
        """
        # stan robota zmienia się na ready
        self._robots_state[robot_id] = robot_State.READY
        # zinkrementować ilość drzew w magazynie o 1 - jest też po stronie UI
        self._stock_pile += 1

    def _update_ready_moving_notEmpty(self, robot_id):
        """
        Ready i aktualny jest moving i misja nie jest pusta
        """
        # stan robota zmienia się na ready
        self._robots_state[robot_id] = robot_State.READY
        # zwalniamy pole z macierzy zajętości
        x = self._current_robots_position[robot_id][0]
        y = self._current_robots_position[robot_id][1]
        self._occupation_matrix[x, y] = '0'
        # zmianiamy aktualną pozycje robota na x', y'
        x_prim = self._next_robots_position[robot_id][0]
        y_prim = self._next_robots_position[robot_id][1]
        self._current_robots_position[robot_id] = [x_prim, y_prim]

    def _update_ready_moving_empty(self, robot_id):
        """
        Ready i aktualny jest moving i misja jest pusta
        """
        # stan robota zmienia się na idle
        self._robots_state[robot_id] = robot_State.IDLE
        # zwalniamy pole z macierzy zajętości
        x = self._current_robots_position[robot_id][0]
        y = self._current_robots_position[robot_id][1]
        self._occupation_matrix[x, y] = '0'
        # zmianiamy aktualną pozycje robota na x', y'
        x_prim = self._next_robots_position[robot_id][0]
        y_prim = self._next_robots_position[robot_id][1]
        self._current_robots_position[robot_id] = [x_prim, y_prim]

    def _update_state_control(self, event):
        """
        W zależnosci od wysyłanego eventu kotrolnego zakutalizuj stan
        """
        l_event = event.split("_")
        if l_event[0] == "move":
            return self._update_state_move(l_event)

        if l_event[0] == "pick":
            return self._update_state_pick(l_event)

        if l_event[0] == "drop":
            return self._update_state_drop(l_event)

    def _update_state_move(self, l_event):
        """
        Zaktualizuj stan w momencie jak wysyłamy move do konkretnego robota
        """
        robot_id = l_event[1]
        x_prim = l_event[2]
        y_prim = l_event[3]
        # stan robota zmienia się na moving
        self._robots_state[robot_id] = robot_State.MOVING
        # zajmujemy pole x_prim y_prim
        self._occupation_matrix[x_prim, y_prim] = 'r'
        # dodajemy następną pozycje robota:
        self._next_robots_position[robot_id] = [x_prim, y_prim]
        # usuwamy zadanie z misji danego robota
        self._missions[robot_id].pop(0)

    def _update_state_pick(self, l_event):
        """
        Zaktualizuj stan w momencie jak wysyłamy pick do konkretnego robota
        """
        robot_id = l_event[1]
        treeID = l_event[1]
        # stan robota zmienia się na collecting
        self._robots_state[robot_id] = robot_State.COLLECTING
        # usuwamy zadanie z misji danego robota
        self._missions[robot_id].pop(0)

    def _update_state_drop(self, l_event):
        """
        Zaktualizuj stan w momencie jak wysyłamy drop do konkretnego robota
        """
        robot_id = l_event[1]
        # stan robota zmienia się na dropping
        self._robots_state[robot_id] = robot_State.DROPPING
        # usuwamy zadanie z misji danego robota
        self._missions[robot_id].pop(0)

    def _select_optimal(self, accepted_event_list):
        """
        Wybierz \"najlepszy\" event z listy zaakceptowanych evetnów (na razie
        może być randomowy)
        """
        pass
