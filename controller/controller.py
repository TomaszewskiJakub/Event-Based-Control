from enum import Enum
import enum
from queue import Empty, Queue
from PySide2 import QtCore
import numpy as np
from numpy.core.records import array
from numpy.lib.function_base import append
from controller.gridGraph import GridGraph
import random
from time import sleep

from model.m_tree import tree_state


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
class ControllerThread(QtCore.QThread):
    def __init__(self, app):
        super(ControllerThread, self).__init__(parent=None)
        self._app = app

    def run(self):
        print("Starting controller")
        self._app.run()


class Controller(QtCore.QObject):
    logMessage = QtCore.Signal(str)

    def __init__(self):
        super(Controller, self).__init__()
        self._current_robots_position = []
        self._next_robots_position = []
        self._robots_state = []
        self._robot_tree = []

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

        self._entrance = None
        self._exit = None
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
        self._width = width
        self._height = height
        self.graph = GridGraph(width+1, height)
        self._drop_position = [width, height//2]
        self._init_robots(robots)
        self._init_trees(trees)
        self._init_occupation_matrix(trees, robots, height, width)
        self._init_missions()
        self._entrance = (width, height-1)
        self._exit = (width, 0)

        # Just for debugging
        # self._generate_mission(0)

    def _init_occupation_matrix(self, trees, robots, height, width):
        """
        Wez listy robotów i drzew z symulatora: trees, robots
        i zainicjalizuj macierz zajetości:
        wolne miejsce - "0"
        robot - "r"
        drzewo - "t"
        """

        tmp_arr = [['0' for i in range(width+1)] for j in range(height)]
        tmp_arr = np.array(tmp_arr)
        self._occupation_matrix = tmp_arr
        for robot in robots:
            self._occupation_matrix[robot.pose[1], robot.pose[0]] = 'r'

        for tree in trees:
            self._occupation_matrix[tree.pose[1], tree.pose[0]] = 't'

        # Just for debugging
        print("Initialized _occupation_matrix: ", self._occupation_matrix)

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
            self._robot_tree.append(0)

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
        self._missions = [[] for i in range(len(self._robots_state))]

        # Just for debugging
        print("Initialized _missions:", self._missions)

    def run(self):
        """
        Głowna pętla programu.
        """
        self.logMessage.emit("Starting controller")
        while(True):
            # print("Executing Controller while")
            acceptable_events = []
            # 1. Przetworz kolejke obserwowalnych i zaktualizuj stan (wywolaj
            #    główną funkcje, w niej iterujemy dopóki kolejka obserwowalnych
            #    nie jest pusta)
            self._update_state_ready()
            # print(" _occupation_matrix: ", self._occupation_matrix)
            # print(" _current_robots_position:", self._current_robots_position)
            # print(" _next_robots_position:", self._next_robots_position)
            # print(" _robots_state:", self._robots_state)
            # print("self._trees_state: ",self._trees_state)
            # print("self._trees_position", self._trees_position)
            # 2. Przejdz po misjach wszystkich robotów
            #   2.1 Jesli pusta wygeneruj
            #   2.2 Jesli nie pusta, weź pierwsze zdanie, sprawdz za pomoca
            #       funcji gamma (dla odpowiedniego eventu) czy jest mozliwa
            #       do wykonania, jeżeli możliwa dodaj do listy mozliwych do
            #       wykonania.
            for robot_id, mission in enumerate(self._missions):
                # print("robot_id: ", robot_id)
                num_free_trees = 0
                for t in self._trees_state:
                    if t == tree_Stete.GROWN:
                        num_free_trees += 1

                if self._robots_state[robot_id] == robot_State.IDLE and num_free_trees > 0:
                    self._missions[robot_id] = self._generate_mission(robot_id)
                    #print("Generate mission for robot:", robot_id)

                if len(self._missions[robot_id]) > 0:
                    event_to_execute = self._missions[robot_id][0]
                    # print("event_to_execute: ", event_to_execute)
                    if self._gamma(event_to_execute):
                        acceptable_events.append(event_to_execute)

            if(all(state == robot_State.IDLE for state in self._robots_state) \
               and num_free_trees == 0):
                break

            # 3. Weź optymalny event z acceptable_events
            # print("acceptable_events", acceptable_events)
            if len(acceptable_events) == 0:
                continue

            event_to_send = self._select_optimal(acceptable_events)
            # przypisujemy assigned do drzewa robota, które ma w swojej misji
            robot_id = int(event_to_send.split("_")[1])
            self._trees_state[self._robot_tree[robot_id]] = tree_Stete.ASSIGNED
            # print("event_to_send: ", event_to_send)
            # 4. Zaktualizuj wewnętrzny stan na podstawie wybranego zadania
            self._update_state_control(event_to_send)
            # 5. Dodaj wybrane zadanie do kolejki controllable_que
            self._controllable_que.put(event_to_send)

            sleep(0.01)

        self.logMessage.emit("No more work to do. Stoping controller")

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
        robot_id = int(l_event[1])
        x_prim = int(l_event[2])
        y_prim = int(l_event[3])

        # jeśli robot może przejeżdzać po drzewach to trzeba dodać '0' or 't'
        if (self._occupation_matrix[y_prim, x_prim] == '0' or
            self._occupation_matrix[y_prim, x_prim] == 't') and \
           (self._robots_state[robot_id] == robot_State.READY or
           self._robots_state[robot_id] == robot_State.IDLE):
            return True
        return False

    def _gamma_pick(self, l_event):
        """
        Sprawdza czy event pick jest możliwy do wykonania
        """
        robot_id = int(l_event[1])
        treeID = int(l_event[2])

        if self._current_robots_position[robot_id] ==\
           self._trees_position[treeID] and \
           self._robots_state[robot_id] == robot_State.READY and\
           self._trees_state[treeID] == tree_Stete.ASSIGNED:
            return True
        return False

    def _gamma_drop(self, l_event):
        """
        Sprawdza czy event drop jest możliwy do wykonania
        """
        robot_id = int(l_event[1])

        if self._current_robots_position[robot_id] == self._drop_position and \
           self._robots_state[robot_id] == robot_State.READY:
            return True
        return False

    def _select_tree(self, robot_id):
        d_min = 1000000
        closest_id = -1
        for tree_id, state in enumerate(self._trees_state):
            if state == tree_Stete.GROWN:
                # print(self._trees_position[tree_id])
                dx = np.abs(self._current_robots_position[robot_id][0]
                            - self._trees_position[tree_id][0])
                dy = np.abs(self._current_robots_position[robot_id][1]
                            - self._trees_position[tree_id][1])
                d = dx+dy
                # print(d)
                if d < d_min:
                    d_min = d
                    closest_id = tree_id
        # print("Closetes: ")
        # print(d_min, self._trees_position[closest_id])

        return closest_id

    def _generate_mission(self, robot_id):
        """
        Generuje całą misje dla danego robota.
        1. Od robota do drzewa i zetnij
        2. Od drzewa do wjadzu
        3. Od wjazdu do magazynu, upusc, od magazynu do wyjazdu
        4. Od wyjzdu do parkingu
        """
        tree_id, path_2_tree = self._mission_collect_tree(robot_id)
        path_2_entrance = self._mission_2_entrance(robot_id, tree_id)
        path_2_road = self._mission_road(robot_id)
        path_2_parking = self._mission_2_parking(robot_id)

        entire_mission = path_2_tree + path_2_entrance + path_2_road + path_2_parking

        # print("path_2_parking: ", path_2_parking)
        # print("Entire misiion:", entire_mission)
        return entire_mission

    def _mission_collect_tree(self, robot_id):
        """
        Generuje ścieżkę od akutalniej pozycji robota do drzewa i dodaje do
        niej event pick.
        1. Wybieramy najbliższe drzewo, które ma stan GROWN

        zwraca ścieżkę i id'k wybranego drzewa
        """
        path = []

        path.append("move_" +
                    str(robot_id) + "_" +
                    str(robot_id) + "_" +
                    str(1))

        path.append("move_" +
                    str(robot_id) + "_" +
                    str(robot_id) + "_" +
                    str(2))

        # tree_id = random.randint(0, len(self._trees_state)-1)
        # while(self._trees_state[tree_id] != tree_Stete.GROWN):
        #     tree_id = random.randint(0, len(self._trees_state)-1)
        tree_id = self._select_tree(robot_id)

        self._robot_tree[robot_id] = tree_id

        desired_tree_position = self._trees_position[tree_id]
        # robot_position = self._current_robots_position[robot_id]
        start = (robot_id, 2)
        goal = tuple(desired_tree_position)

        came_from, cost_so_far = self.graph.a_star_search(self.graph,
                                                          start, goal)
        # self.graph.draw_grid(self.graph,
        #                      point_to=came_from,
        #                      start=start, goal=goal)
        # self.graph.draw_grid(self.graph,
        #                      path=self.graph.reconstruct_path(came_from,
        #                                                       start=start,
        #                                                       goal=goal))

        mission = self.graph.reconstruct_path(came_from,
                                              start=start,
                                              goal=goal)
        mission.pop(0)
        path += ["move_" +
                 str(robot_id) + "_" +
                 str(position[0]) + "_" +
                 str(position[1]) for position in mission]
        # Equivalence in standard for loop
        # for position in mission:
        #     path.append("move_" +
        #                 str(robot_id) + "_" +
        #                 str(position[0]) + "_" +
        #                 str(position[1]))

        path.append("pick_" +
                    str(robot_id) + "_" +
                    str(tree_id))

        # print("Mission: ", mission)
        # print("Path:", path)

        return tree_id, path

    def _mission_2_entrance(self, robot_id, tree_id):
        """
        Generuje ścieżkę od wybranwgo drzewa do wjazdu (żeby stanął na
        pierwszym kafelku drogi).
        """
        path = []
        tree_position = self._trees_position[tree_id]

        start = tuple(tree_position)
        goal = self._entrance

        came_from, cost_so_far = self.graph.a_star_search(self.graph,
                                                          start, goal)
        # self.graph.draw_grid(self.graph,
        #                      point_to=came_from,
        #                      start=start, goal=goal)
        # self.graph.draw_grid(self.graph,
        #                      path=self.graph.reconstruct_path(came_from,
        #                                                       start=start,
        #                                                       goal=goal))
        mission = self.graph.reconstruct_path(came_from,
                                              start=start,
                                              goal=goal)

        mission.pop(0)
        path = ["move_" +
                str(robot_id) + "_" +
                str(position[0]) + "_" +
                str(position[1]) for position in mission]
        # Equivalence in standard for loop
        # for position in mission:
        #     path.append("move_" +
        #                 str(robot_id) + "_" +
        #                 str(position[0]) + "_" +
        #                 str(position[1]))

        # print("Mission:", mission)
        # print("Path:", path)

        return path

    def _mission_road(self, robot_id):
        """
        Generuj ruch po drodze do magazynu, odstawienie drzewa, i ruch od
        magazynu do wyjazdu (żeby stanął na ostatnim kafelku drogi).
        """
        path = []
        start = self._entrance
        goal = tuple(self._drop_position)

        came_from, cost_so_far = self.graph.a_star_search(self.graph,
                                                          start, goal)
        # self.graph.draw_grid(self.graph,
        #                      point_to=came_from,
        #                      start=start, goal=goal)
        # self.graph.draw_grid(self.graph,
        #                      path=self.graph.reconstruct_path(came_from,
        #                                                       start=start,
        #                                                       goal=goal))

        mission_to_drop = self.graph.reconstruct_path(came_from,
                                                      start=start,
                                                      goal=goal)
        mission_to_drop.pop(0)

        start = tuple(self._drop_position)
        goal = self._exit

        came_from, cost_so_far = self.graph.a_star_search(self.graph,
                                                          start, goal)
        # self.graph.draw_grid(self.graph,
        #                      point_to=came_from,
        #                      start=start, goal=goal)
        # self.graph.draw_grid(self.graph,
        #                      path=self.graph.reconstruct_path(came_from,
        #                                                       start=start,
        #                                                       goal=goal))

        mission_to_exit = self.graph.reconstruct_path(came_from,
                                                      start=start,
                                                      goal=goal)
        mission_to_exit.pop(0)
        # print("Mission_to_drop:", mission_to_drop)
        # print("Mission_to_exit:", mission_to_exit)

        path = ["move_" +
                str(robot_id) + "_" +
                str(position[0]) + "_" +
                str(position[1]) for position in mission_to_drop]
        # Equivalence in standard for loop
        # for position in mission_to_drop:
        #     path.append("move_" +
        #                 str(robot_id) + "_" +
        #                 str(position[0]) + "_" +
        #                 str(position[1]))

        path.append("drop_" + str(robot_id))

        path += ["move_" +
                 str(robot_id) + "_" +
                 str(position[0]) + "_" +
                 str(position[1]) for position in mission_to_exit]
        # Equivalence in standard for loop
        # for position in mission_to_exit:
        #     path.append("move_" +
        #                 str(robot_id) + "_" +
        #                 str(position[0]) + "_" +
        #                 str(position[1]))

        # print("Path: ", path)

        return path

    def _mission_2_parking(self, robot_id):
        """
        Generuj ruch od aktualniej pozycji robota do jego miejsca w parkingu
        """
        path = []

        for i in range(self._width - len(self._robots_state)):
            path.append("move_" +
                        str(robot_id) + "_" +
                        str(self._width-1-i) + "_" +
                        str(0))

        path.append("move_" +
                    str(robot_id) + "_" +
                    str(len(self._robots_state)) + "_" +
                    str(1))

        for i in range(len(self._robots_state) - robot_id):
            path.append("move_" +
                        str(robot_id) + "_" +
                        str(len(self._robots_state)-1-i) + "_" +
                        str(1))

        path.append("move_" +
                    str(robot_id) + "_" +
                    str(robot_id) + "_" +
                    str(0))

        # # the robot position is still the robot position on the parking
        # robot_position = self._current_robots_position[robot_id]
        # start = self._exit
        # goal = tuple(robot_position)

        # came_from, cost_so_far = self.graph.a_star_search(self.graph,
        #                                                   start, goal)
        # # self.graph.draw_grid(self.graph,
        # #                      point_to=came_from,
        # #                      start=start, goal=goal)
        # # self.graph.draw_grid(self.graph,
        # #                      path=self.graph.reconstruct_path(came_from,
        # #                                                       start=start,
        # #                                                       goal=goal))
        # mission = self.graph.reconstruct_path(came_from,
        #                                       start=start,
        #                                       goal=goal)
        # mission.pop(0)

        # path = ["move_" +
        #         str(robot_id) + "_" +
        #         str(position[0]) + "_" +
        #         str(position[1]) for position in mission]
        # # Equivalence in standard for loop
        # # for position in mission:
        # #     path.append("move_" +
        # #                 str(robot_id) + "_" +
        # #                 str(position[0]) + "_" +
        # #                 str(position[1]))

        # # print("Mission:", mission)
        # # print("Path: ", path)

        return path

    def _update_state_ready(self):
        """
        Przetwarzaj tak długo jak kolejka obserwowalnych nie jest pusta.
        Aktualizuj stan na podstawie aktualnego stanu.
        """
        while not self._observable_que.empty():
            event = self._observable_que.get_nowait()
            l_event = event.split("_")
            robot_id = int(l_event[1])

            if self._robots_state[robot_id] == robot_State.COLLECTING:
                self._update_ready_collecting(robot_id)

            if self._robots_state[robot_id] == robot_State.DROPPING:
                self._update_ready_dropping(robot_id)

            if self._robots_state[robot_id] == robot_State.MOVING and\
               len(self._missions[robot_id]) > 0:
                self._update_ready_moving_notEmpty(robot_id)

            if self._robots_state[robot_id] == robot_State.MOVING and\
               len(self._missions[robot_id]) == 0:
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
        self._occupation_matrix[y, x] = '0'
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
        self._occupation_matrix[y, x] = '0'
        # zmianiamy aktualną pozycje robota na x', y'
        x_prim = self._next_robots_position[robot_id][0]
        y_prim = self._next_robots_position[robot_id][1]
        self._current_robots_position[robot_id] = [x_prim, y_prim]

        self._missions[robot_id] = []

    def _update_state_control(self, event):
        """
        W zależnosci od wysyłanego eventu kotrolnego zakutalizuj stan
        """
        l_event = event.split("_")
        if l_event[0] == "move":
            self._update_state_move(l_event)

        if l_event[0] == "pick":
            self._update_state_pick(l_event)

        if l_event[0] == "drop":
            self._update_state_drop(l_event)

    def _update_state_move(self, l_event):
        """
        Zaktualizuj stan w momencie jak wysyłamy move do konkretnego robota
        """
        robot_id = int(l_event[1])
        x_prim = int(l_event[2])
        y_prim = int(l_event[3])
        # stan robota zmienia się na moving
        self._robots_state[robot_id] = robot_State.MOVING
        # zajmujemy pole x_prim y_prim
        self._occupation_matrix[y_prim, x_prim] = 'r'
        # dodajemy następną pozycje robota:
        self._next_robots_position[robot_id] = [x_prim, y_prim]
        # usuwamy zadanie z misji danego robota
        self._missions[robot_id].pop(0)

    def _update_state_pick(self, l_event):
        """
        Zaktualizuj stan w momencie jak wysyłamy pick do konkretnego robota
        """
        robot_id = int(l_event[1])
        treeID = int(l_event[1])
        # stan robota zmienia się na collecting
        self._robots_state[robot_id] = robot_State.COLLECTING
        # usuwamy zadanie z misji danego robota
        self._missions[robot_id].pop(0)

    def _update_state_drop(self, l_event):
        """
        Zaktualizuj stan w momencie jak wysyłamy drop do konkretnego robota
        """
        robot_id = int(l_event[1])
        # stan robota zmienia się na dropping
        self._robots_state[robot_id] = robot_State.DROPPING
        # usuwamy zadanie z misji danego robota
        self._missions[robot_id].pop(0)

    def _select_optimal(self, accepted_event_list):
        """
        Wybierz \"najlepszy\" event z listy zaakceptowanych evetnów (na razie
        może być randomowy)
        """
        return random.choice(accepted_event_list)
