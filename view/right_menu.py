from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIntValidator
from view.about_window import AboutWindow

class RightMenu(QtWidgets.QGroupBox):
    sendData = QtCore.Signal(int, int, int, int)

    def __init__(self):
        super(RightMenu, self).__init__("Menu")

        self._main_layout = QtWidgets.QVBoxLayout()
        self._world_layout = QtWidgets.QVBoxLayout()
        self._world_fields_layout = QtWidgets.QGridLayout()
        self._robots_layout = QtWidgets.QHBoxLayout()
        self._trees_layout = QtWidgets.QHBoxLayout()
        self._button_layout = QtWidgets.QHBoxLayout()

        self._world_label = QtWidgets.QLabel("World size:")
        self._x_label = QtWidgets.QLabel("x:")
        self._y_label = QtWidgets.QLabel("y:")
        self._x_textbox = QtWidgets.QLineEdit()
        self._y_textbox = QtWidgets.QLineEdit()
        self._world_validator = QIntValidator(10, 50)

        self._robots_label = QtWidgets.QLabel("Number of robots:")
        self._robots_textbox = QtWidgets.QLineEdit()
        self._robots_validator = QIntValidator(1, 10)

        self._trees_label = QtWidgets.QLabel("Number of trees:   ")
        self._trees_textbox = QtWidgets.QLineEdit()
        self._trees_validator = QIntValidator(1, 2000)

        self._create_button = QtWidgets.QPushButton("Create")
        self._clear_button = QtWidgets.QPushButton("Clear")
        self._default_button = QtWidgets.QPushButton("Default")
        self._about_button = QtWidgets.QPushButton("About")

        self._initUI()

    def _initUI(self):
        # verticalSpacer = QtWidgets.QSpacerItem(
        #         10, 10,
        #         QtWidgets.QSizePolicy.Minimum,
        #         QtWidgets.QSizePolicy.Expanding)

        # self._x_textbox.validator = self._world_validator
        # self._y_textbox.validator = self._world_validator
        # self._x_textbox.maxLength = 10
        # self._y_textbox.maxLength = 10

        # self._x_textbox.setSizePolicy(
        #     QtWidgets.QSizePolicy.Minimum,
        #     QtWidgets.QSizePolicy.Minimum
        # )
        # self._y_textbox.setSizePolicy(
        #     QtWidgets.QSizePolicy.Minimum,
        #     QtWidgets.QSizePolicy.Minimum
        # )
        # self._robots_textbox.setSizePolicy(
        #     QtWidgets.QSizePolicy.Minimum,
        #     QtWidgets.QSizePolicy.Minimum
        # )
        # self._trees_textbox.setSizePolicy(
        #     QtWidgets.QSizePolicy.Minimum,
        #     QtWidgets.QSizePolicy.Minimum
        # )

        self._world_fields_layout.addWidget(self._x_label, 0, 0)
        self._world_fields_layout.addWidget(self._y_label, 1, 0)
        self._world_fields_layout.addWidget(self._x_textbox, 0, 1)
        self._world_fields_layout.addWidget(self._y_textbox, 1, 1)

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
        # self._main_layout.addSpacerItem(verticalSpacer)

        self.setLayout(self._main_layout)

        self._create_button.clicked.connect(self._create_clicked)
        self._clear_button.clicked.connect(self._clear_clicked)
        self._default_button.clicked.connect(self._default_clicked)

        self._about_button.clicked.connect(self._about_clicked)
        self._about_window = AboutWindow()

    @QtCore.Slot()
    def _create_clicked(self):
        self.sendData.emit(
            int(self._x_textbox.text()),
            int(self._y_textbox.text()),
            int(self._robots_textbox.text()),
            int(self._trees_textbox.text())
        )
        self._x_textbox.setDisabled(True)
        self._y_textbox.setDisabled(True)
        self._robots_textbox.setDisabled(True)
        self._trees_textbox.setDisabled(True)

        self._create_button.setDisabled(True)
        self._clear_button.setDisabled(True)
        self._default_button.setDisabled(True)

    @QtCore.Slot()
    def _clear_clicked(self):
        self._x_textbox.clear()
        self._y_textbox.clear()
        self._robots_textbox.clear()
        self._trees_textbox.clear()

    @QtCore.Slot()
    def _default_clicked(self):
        self._x_textbox.setText(str(25))
        self._y_textbox.setText(str(25))
        self._robots_textbox.setText(str(5))
        self._trees_textbox.setText(str(50))

    @QtCore.Slot()
    def _about_clicked(self):
        self._about_window.show()

    def validate_inputs(self):
        pass
