from enum import Enum
from queue import Queue
from PySide2 import QtCore


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
#    move_robotID_x'_y'
#    pick_robotID_treeID
#    drop_robotID
#    ready_robotID
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

    @property
    def observable_que(self):
        return self._observable_que

    @property
    def controllable_que(self):
        return self._controllable_que

    @controllable_que.setter
    def controlable_que(self, var):
        self._controllable_que = var

    @QtCore.Slot()
    def init_all(self, trees, robots, height, width):
        """
        Sygnał inicializujący Controller
        """
        print("initing controller")
        # self._init_robots()
        # self._init_robots()
        # self._init_occupation_matrix()
        # self._init_missions()

    def _init_occupation_matrix(self, tree, robots):
        """
        Wez listy robotów i drzew z symulatora: trees, robots
        i zainicjalizuj macierz zajetości:
        wolne miejsce - "0"
        robot - "r"
        drzewo - "t"
        """

    def _init_robots(self, robots):
        """
        Wez liste robotów  z symulatora: robots
        i zainicjalizuj  current_robots_position,
        next_robots_position oraz robots_state
        """
        pass

    def _init_trees(self, trees):
        """
        Wez liste drzew  z symulatora: trees
        i zainicjalizuj trees_position oraz trees_state
        """
        pass

    def _init_missions(self):
        """
        zainicjalizuj puste listy 
        Misje będą wysznaczane w pętli programu:
        Zawsze kiedy program sprawdzi że jakiś robot ma pustą misje
        to wyznaczy mu nową,
        Tak więc w pierwszej iteracji programu zostaną wyznaczone
        misje dla wszystkich robotów
        """
        pass

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
        pass

    def _gamma_move(self, event):
        """
        Sprawdza czy event move jest możliwy do wykonania
        """
        pass

    def _gamma_pick(self, event):
        """
        Sprawdza czy event pick jest możliwy do wykonania
        """
        pass

    def _gamma_drop(self, event):
        """
        Sprawdza czy event drop jest możliwy do wykonania
        """
        pass

    def _generate_mission(self, robot_id):
        """
        Generuje całą misje dla danego robota.
        1. Od robota do drzewa i zetnij
        2. Od drzewa do wjadzu
        3. Od wjazdu do magazynu, upusc, od magazynu do wyjazdu
        4. Od wyjzdu do parkingu
        """
        pass

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
        Generuje ścieżkę od wybranwgo drzewa do wjazdu (żeby stanął na pierwszym
        kafelku drogi).
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
        pass

    def _update_ready_collecting(self):
        """
        Ready i aktualny stan collecting
        """
        pass

    def _update_ready_dropping(self):
        """
        Ready i aktualny stan dropping
        """
        pass

    def _update_ready_moving_notEmpty(self):
        """
        Ready i aktualny jest moving i misja nie jest pusta
        """
        pass

    def _update_ready_moving_empty(self):
        """
        Ready i aktualny jest moving i misja jest pusta
        """
        pass

    def _update_state_control(self, event):
        """
        W zależnosci od wysyłanego eventu kotrolnego zakutalizuj stan
        """
        pass

    def _update_state_move(self, event):
        """
        Zaktualizuj stan w momencie jak wysyłamy move do konkretnego robota
        """
        pass

    def _update_state_pick(self, event):
        """
        Zaktualizuj stan w momencie jak wysyłamy pick do konkretnego robota
        """
        pass

    def _update_state_drop(self, event):
        """
        Zaktualizuj stan w momencie jak wysyłamy drop do konkretnego robota
        """
        pass

    def _select_optimal(self, accepted_event_list):
        """
        Wybierz \"najlepszy\" event z listy zaakceptowanych evetnów (na razie
        może być randomowy)
        """
        pass
