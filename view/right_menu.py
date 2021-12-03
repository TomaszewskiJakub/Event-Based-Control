from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIntValidator
from view.about_window import AboutWindow


class RightMenu(QtWidgets.QGroupBox):
    sendData = QtCore.Signal(int, int, int, int)
    logMessage = QtCore.Signal(str)

    def __init__(self):
        super(RightMenu, self).__init__("Menu")

        self._main_layout = QtWidgets.QVBoxLayout()
        self._world_layout = QtWidgets.QVBoxLayout()
        self._world_fields_layout = QtWidgets.QGridLayout()
        self._robots_layout = QtWidgets.QHBoxLayout()
        self._trees_layout = QtWidgets.QHBoxLayout()
        self._button_layout = QtWidgets.QHBoxLayout()

        self._world_label = QtWidgets.QLabel("World size:")
        self._height_label = QtWidgets.QLabel("height:")
        self._width_label = QtWidgets.QLabel("width:")
        self._height_textbox = QtWidgets.QLineEdit()
        self._width_textbox = QtWidgets.QLineEdit()

        self._robots_label = QtWidgets.QLabel("Number of robots:")
        self._robots_textbox = QtWidgets.QLineEdit()

        self._trees_label = QtWidgets.QLabel("Number of trees:   ")
        self._trees_textbox = QtWidgets.QLineEdit()
        self._trees_validator = QIntValidator(1, 2000)

        self._create_button = QtWidgets.QPushButton("Create")
        self._clear_button = QtWidgets.QPushButton("Clear")
        self._default_button = QtWidgets.QPushButton("Default")
        self._about_button = QtWidgets.QPushButton("About")

        self._initUI()

    def _initUI(self):
        self._world_fields_layout.addWidget(self._height_label, 0, 0)
        self._world_fields_layout.addWidget(self._width_label, 1, 0)
        self._world_fields_layout.addWidget(self._height_textbox, 0, 1)
        self._world_fields_layout.addWidget(self._width_textbox, 1, 1)

        self._world_layout.addWidget(self._world_label)
        self._world_layout.addLayout(self._world_fields_layout)

        self._robots_layout.addWidget(self._robots_label)
        self._robots_layout.addWidget(self._robots_textbox)

        self._trees_layout.addWidget(self._trees_label)
        self._trees_layout.addWidget(self._trees_textbox)

        self._button_layout.addWidget(self._create_button)
        self._button_layout.addWidget(self._clear_button)
        self._button_layout.addWidget(self._default_button)

        self._main_layout.addLayout(self._world_layout)
        self._main_layout.addLayout(self._robots_layout)
        self._main_layout.addLayout(self._trees_layout)
        self._main_layout.addLayout(self._button_layout)
        self._main_layout.addWidget(self._about_button)

        self.setLayout(self._main_layout)

        self._create_button.clicked.connect(self._create_clicked)
        self._clear_button.clicked.connect(self._clear_clicked)
        self._default_button.clicked.connect(self._default_clicked)

        self._about_button.clicked.connect(self._about_clicked)
        self._about_window = AboutWindow()

    @QtCore.Slot()
    def _create_clicked(self):
        width = int(self._width_textbox.text())
        height = int(self._height_textbox.text())
        num_robots = int(self._robots_textbox.text())
        num_trees = int(self._trees_textbox.text())

        try:
            self.validate_inputs(width, height, num_robots, num_trees)
        except RuntimeError as e:
            self.logMessage.emit(str(e))
            return

        self.sendData.emit(
            width,
            height,
            num_robots,
            num_trees
        )
        self._height_textbox.setDisabled(True)
        self._width_textbox.setDisabled(True)
        self._robots_textbox.setDisabled(True)
        self._trees_textbox.setDisabled(True)

        self._create_button.setDisabled(True)
        self._clear_button.setDisabled(True)
        self._default_button.setDisabled(True)

    @QtCore.Slot()
    def _clear_clicked(self):
        self._height_textbox.clear()
        self._width_textbox.clear()
        self._robots_textbox.clear()
        self._trees_textbox.clear()

    @QtCore.Slot()
    def _default_clicked(self):
        self._height_textbox.setText(str(25))
        self._width_textbox.setText(str(25))
        self._robots_textbox.setText(str(5))
        self._trees_textbox.setText(str(50))

    @QtCore.Slot()
    def _about_clicked(self):
        self._about_window.show()

    def validate_inputs(self, width, height, num_robots, num_trees):
        if(width < 10 or width > 50):
            raise RuntimeError("Wrong width (10 < w < 50)!")
        if(height < 10 or height > 50):
            raise RuntimeError("Wrong height (10 < h < 50)!")

        # We assume that the bridge has length 3 and each segment takes 4 wood
        # so we need at least 12 wood
        if(num_trees < 12):
            raise RuntimeError("Not enough trees (min. 12)!")

        # If there is fewer places where trees can spawn than the number of trees
        if((width-3)*(height-4) < num_trees):
            raise RuntimeError("Not enough spawning spaces for trees")

        # We need to have at least 1 robot and at most (width-3) robots
        if(num_robots < 1 or num_robots > width-3):
            raise RuntimeError("Wrong number of robots (1 <= r < w-3)!")
