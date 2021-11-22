from PySide2 import QtCore, QtWidgets
import re


class Console(QtWidgets.QWidget):
    def __init__(self, simulator, controller):
        super(Console, self).__init__()

        self._text_box = QtWidgets.QTextEdit()
        self._input_line = QtWidgets.QLineEdit()
        self._send_button = QtWidgets.QPushButton("Send")

        self._input_layout = QtWidgets.QHBoxLayout()
        self._main_layout = QtWidgets.QVBoxLayout()

        self._simulator = simulator
        self._controller = controller

        self._move_re = re.compile("^move_\d+_\d+_\d+$")
        self._pick_re = re.compile("^pick_\d+_\d+$")
        self._drop_re = re.compile("^drop_\d+$")
        self._ready_re = re.compile("^ready_\d+$")

        self._initUI()

    def _initUI(self):
        self._text_box.setReadOnly(True)
        self._main_layout.addWidget(QtWidgets.QLabel("Console"))
        self._main_layout.addWidget(self._text_box)
        self._input_layout.addWidget(self._input_line)
        self._input_layout.addWidget(self._send_button)
        self._main_layout.addLayout(self._input_layout)

        self._send_button.clicked.connect(self._send_command)

        self.setLayout(self._main_layout)

    @QtCore.Slot()
    def add_log(self, msg):
        self._text_box.append(msg)

    @QtCore.Slot()
    def _send_command(self):
        command = self._input_line.text()
        self._parse_command(command)

    def _parse_command(self, command):
        if "ready" in command:
            if(self._ready_re.match(command)):
                self._text_box.append("Sending " + command + " to controller!")
                self._controller._observable_que.put(command)
            else:
                self._text_box.append("Invalid structure of ready! It should be: ready_RobotID")
            pass
        elif("move" in command):
            if(self._move_re.match(command)):
                self._text_box.append("Sending " + command + " to simulator!")
                self._simulator._controllable_que.put(command)
            else:
                self._text_box.append("Invalid structure of move! It should be: move_RobotID_X'_Y'")
        elif("pick" in command):
            if(self._pick_re.match(command)):
                self._text_box.append("Sending " + command + " to simulator!")
                self._simulator._controllable_que.put(command)
            else:
                self._text_box.append("Invalid structure of pick! It should be: pick_RobotID_TreeID")
        elif("drop" in command):
            if(self._drop_re.match(command)):
                self._text_box.append("Sending " + command + " to simulator!")
                self._simulator._controllable_que.put(command)
            else:
                self._text_box.append("Invalid structure of drop! It should be: drop_RobotID")
        else:
            self._text_box.append("Unrecognized command!")

        self._input_line.clear()
